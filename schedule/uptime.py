from datetime import datetime, timedelta, time, timezone
import requests

from django.db import transaction
from django.conf import settings
from schedule.models import Downtime
from schedule.configdb import configdb
from rise_set.visibility import Visibility
from rise_set.angle import Angle
from time_intervals.intervals import Intervals


HOURS_PER_DEGREES = 15


class UptimeException(Exception):
    pass


def get_semesters(date_from: datetime, date_to: datetime):
    """
    Gets the set of semesters from the Observation Portal that includes the range of dates specified.

    Returns a list of semesters, even if there is only one.
    """
    try:
        response = requests.get(settings.OBS_PORTAL_URL + f'/api/semesters/?end_gt={date_from.isoformat()}&start_lte={date_to.isoformat()}', timeout=120)
        response.raise_for_status()
        # convert semester bounds to python dates
        results = response.json()['results']
        for result in results:
            result['start'] = datetime.fromisoformat(result['start'].replace('Z', '+00:00'))
            result['end'] = datetime.fromisoformat(result['end'].replace('Z', '+00:00'))
        return results
    except Exception as e:
        print(f"Failed to get Semesters from {settings.OBS_PORTAL_URL}: {repr(e)}")
        raise UptimeException(e)


def get_existing_uptimes_for_semester(site: str, enclosure: str, telescope: str, instrument_type: str, semester: dict):
    # To get the uptimes for a semester, we first get the downtimes in the semester, then inverse to get uptimes
    downtimes = Downtime.objects.filter(site=site, enclosure=enclosure, telescope=telescope,
                                        instrument_type=instrument_type, start__lt=semester['end'],
                                        end__gt=semester['start'])
    return convert_downtimes_to_uptimes(downtimes, semester['start'], semester['end'])




def convert_downtimes_to_uptimes(downtimes, date_from, date_to):
    """
    Converts downtimes to uptimes.

    Takes in a queryset of downtimes, and a bounding date range, and returns an Intervals set of
    the complement, i.e. the uptimes within that bounding date range.
    If bounding dates are not specified, attempt to use Downtimes themselves to get the bounding range.
    """
    intervals = []
    for downtime in downtimes:
        intervals.append((downtime.start, downtime.end))
    if not intervals:
        # If we receive no current downtimes in the semester, then assume the whole time is downtime!
        intervals.append((date_from, date_to))
    intervalset = Intervals(intervals)
    # Take the complement of the downtime intervals to get the uptimes
    intervalset.complement(date_from, date_to)
    return intervalset


def replace_schedule_for_semester(site: str, enclosure: str, telescope: str, instrument_type: str,
                                  reason: str, downtime_intervals: list, semester: dict):
    """
    Replaces current semester schedule on resource with new set of downtime intervals.

    This function takes in a list of intervals of downtime for a specific resource and a semester
    and in an atomic transaction deletes all existing downtimes on that resource and creates the new ones.
    """
    downtimes = []
    for interval in downtime_intervals:
        downtimes.append(Downtime(
            start=interval[0],
            end=interval[1],
            site=site,
            enclosure=enclosure,
            telescope=telescope,
            instrument_type=instrument_type,
            reason=reason))
    with transaction.atomic():
        # Now in an atomic transaction, delete existing Downtimes and create the new set for this resource
        Downtime.objects.filter(site=site, enclosure=enclosure, telescope=telescope,
                                instrument_type=instrument_type, start__lt=semester['end'],
                                end__gt=semester['start']).delete()
        Downtime.objects.bulk_create(downtimes, batch_size=100)


def modify_schedule_with_uptimes(uptimes_group: list):
    """
    Modifies existing downtimes based on input uptimes on resources.

    Takes output of UptimesSerializer and calculates the exact uptime windows using rise_set, then merges
    those windows with the existing downtimes, then replaces the set of downtimes for the semester and resource.
    """
    # Do the following for each unique set of site/enclosure/telescope/instrument_type:
    for uptime_group in uptimes_group:
        tz = configdb.get_site_timezone(uptime_group['site'])
        telescope_info = configdb.get_telescope_info(uptime_group['site'], uptime_group['enclosure'],
                                                     uptime_group['telescope'], uptime_group['instrument_type'])
        rise_set_site = {
            'latitude': Angle(degrees=telescope_info['latitude']),
            'longitude': Angle(degrees=telescope_info['longitude']),
            'horizon': Angle(degrees=telescope_info['horizon']),
            'ha_limit_neg': Angle(degrees=telescope_info['ha_limit_neg'] * HOURS_PER_DEGREES),
            'ha_limit_pos': Angle(degrees=telescope_info['ha_limit_pos'] * HOURS_PER_DEGREES)
        }
        earliest_date = datetime.max.replace(tzinfo=timezone.utc)
        latest_date = datetime.min.replace(tzinfo=timezone.utc)
        for uptime in uptime_group['uptimes']:
            # Translate the day into a start time before the start of night in UTC for that site
            start = datetime.combine(uptime['day'], time(22 + tz)).replace(tzinfo=timezone.utc)
            # Keep track of the earliest and latest dates we want to set for this resource
            # To help us figure out the semester(s) these changes are within later
            earliest_date = min(start, earliest_date)
            latest_date = max(start, latest_date)
            visibility = Visibility(
                site=rise_set_site,
                start_date=start,
                end_date=start + timedelta(hours=24),
                horizon=telescope_info['horizon'],
                ha_limit_neg=telescope_info['ha_limit_neg'],
                ha_limit_pos=telescope_info['ha_limit_pos'],
                twilight='nautical'
            )
            interval = visibility.get_dark_intervals()[0]
            late_start = timedelta(minutes=uptime['late_start'])
            early_end = timedelta(minutes=uptime['early_end'])
            if uptime['portion_of_night'] != 'all':
                # Get the half interval duration, needed to calculate partial nights
                half_interval_duration = (interval[1] - interval[0]) / 2
                if uptime['portion_of_night'] == 'first_half':
                    interval = (interval[0] + late_start, interval[1] - half_interval_duration)
                elif uptime['portion_of_night'] == 'second_half':
                    interval = (interval[0] + half_interval_duration, interval[1] - early_end)
            else:
                interval = (interval[0] + late_start, interval[1] - early_end)
            # Place the rise_set adjusted night interval into the uptime object to use later
            uptime['interval'] = interval

        # Get the semester(s) bounds that these requested changes are within
        semesters = get_semesters(earliest_date.replace(tzinfo=None), latest_date.replace(tzinfo=None))
        # Then get the existing downtimes within the semester bounds (from obs portal) of all these
        # Create a set of time intervals from the existing uptimes (inverse of existing downtimes)
        for semester in semesters:
            existing_uptimes = get_existing_uptimes_for_semester(
                uptime_group['site'], uptime_group['enclosure'], uptime_group['telescope'],
                uptime_group['instrument_type'], semester)

            # add in the new ones to add, and subtract out the new ones to remove
            uptimes_to_remove = []
            uptimes_to_add = []
            for uptime in uptime_group['uptimes']:
                # If this uptime change is within the current semester, then do something with it
                if semester['start'] <= datetime.combine(uptime['day'], time(0)).replace(tzinfo=timezone.utc) <= semester['end']:
                    if uptime['remove']:
                        uptimes_to_remove.append(uptime['interval'])
                    else:
                        uptimes_to_add.append(uptime['interval'])
            existing_uptimes.add(uptimes_to_add)
            if uptimes_to_remove:
                intervalset_to_remove = Intervals(uptimes_to_remove)
                existing_uptimes = existing_uptimes.subtract(intervalset_to_remove)
            
            # Inverse the set of available intervals within the semester bounds of their datetime (from obs portal) to get a set of downtimes
            existing_uptimes.complement(semester['start'], semester['end'])
    
            # In a single database transaction, delete the existing downtimes within the semester bounds for this instrument type, and create the new set.
            replace_schedule_for_semester(uptime_group['site'], uptime_group['enclosure'], uptime_group['telescope'],
                                          uptime_group['instrument_type'], uptime_group['reason'],
                                          existing_uptimes.toTupleList(), semester)
