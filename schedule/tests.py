from datetime import timedelta, datetime, date, timezone as dt_timezone
import copy
import json
from unittest.mock import patch

from django.test import TestCase
from django.utils import timezone
from django.urls import reverse
from django.contrib.auth.models import User

from schedule.models import Downtime


class TestModelAdmin(TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.admin_user = User.objects.create_superuser('admin', 'admin@example.com', 'admin')
        self.client.force_login(self.admin_user)

    @staticmethod
    def _get_post_data_for_new_downtime(start, end):
        return {
            'reason': 'Maintenance',
            'site': 'tst',
            'enclosure': 'doma',
            'telescope': '1m0a',
            # POST data to the model admin add view expect that model fields that are
            # DateTimeFields are separated by date and time as follows
            'start_0': start.date(),
            'start_1': start.time(),
            'end_0': end.date(),
            'end_1': end.time(),
        }

    def test_add_downtime(self):
        start = timezone.now() - timedelta(days=2)
        end = start + timedelta(hours=1)
        data = self._get_post_data_for_new_downtime(start, end)
        self.assertEqual(Downtime.objects.count(), 0)
        self.client.post(reverse('admin:schedule_downtime_add'), data, follow=True)
        self.assertEqual(Downtime.objects.count(), 1)

    def test_downtime_with_end_before_start_not_allowed(self):
        start = timezone.now() - timedelta(days=2)
        end = start - timedelta(hours=1)
        data = self._get_post_data_for_new_downtime(start, end)
        self.assertEqual(Downtime.objects.count(), 0)
        response = self.client.post(reverse('admin:schedule_downtime_add'), data, follow=True)
        self.assertEqual(Downtime.objects.count(), 0)
        self.assertIn('End time must be after start time', str(response.content))


class TestDowntimeSerializer(TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.base_downtime = {
            'start': '2020-10-10T20:10:10Z',
            'end': '2020-10-10T21:22:22Z',
            'site': 'tst',
            'enclosure': 'doma',
            'telescope': '1m0a'
        }
        self.admin_user = User.objects.create_superuser('admin', 'admin@example.com', 'admin')
        self.normal_user = User.objects.create_user('normal', 'normal@example.com', 'normal')
        self.client.force_login(self.admin_user)

    def test_post_downtime(self):
        downtime = copy.deepcopy(self.base_downtime)
        self.assertEqual(Downtime.objects.count(), 0)
        response = self.client.post(reverse('downtime-list'), downtime)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Downtime.objects.count(), 1)
        self.assertIn('instrument_type', response.json())
        self.assertEqual(response.json()['instrument_type'], '')

    def test_post_downtime_fails_if_not_logged_in(self):
        self.client.logout()
        downtime = copy.deepcopy(self.base_downtime)
        self.assertEqual(Downtime.objects.count(), 0)
        self.client.post(reverse('downtime-list'), downtime)
        self.assertEqual(Downtime.objects.count(), 0)

    def test_post_downtime_fails_if_not_authenticated_user(self):
        self.client.logout()
        downtime = copy.deepcopy(self.base_downtime)
        self.assertEqual(Downtime.objects.count(), 0)
        response = self.client.post(reverse('downtime-list'), downtime)
        self.assertEqual(response.status_code, 401)  # check that the request was unauthorized
        self.assertEqual(Downtime.objects.count(), 0)
        # Now test for an authenticated normal user
        self.client.force_login(self.normal_user)
        downtime = copy.deepcopy(self.base_downtime)
        self.assertEqual(Downtime.objects.count(), 0)
        response = self.client.post(reverse('downtime-list'), downtime)
        self.assertEqual(response.status_code, 201)  # check that the request worked
        self.assertEqual(Downtime.objects.count(), 1)

    def test_post_downtime_fails_invalid_site(self):
        downtime = copy.deepcopy(self.base_downtime)
        downtime['site'] = 'nop' # this site doesnt exist in the test configdb data
        self.assertEqual(Downtime.objects.count(), 0)
        response = self.client.post(reverse('downtime-list'), downtime)
        self.assertEqual(Downtime.objects.count(), 0)
        self.assertIn('site', response.json())
        self.assertIn('"nop" is not a valid choice', response.json()['site'][0])

    def test_post_downtime_fails_invalid_instrument_type(self):
        downtime = copy.deepcopy(self.base_downtime)
        downtime['instrument_type'] = 'nop' # this instrument_type doesnt exist in the test configdb data
        self.assertEqual(Downtime.objects.count(), 0)
        response = self.client.post(reverse('downtime-list'), downtime)
        self.assertEqual(Downtime.objects.count(), 0)
        self.assertIn('instrument_type', response.json())
        self.assertIn('"nop" is not a valid choice', response.json()['instrument_type'][0])

    def test_post_downtime_fails_invalid_telescope_combo(self):
        downtime = copy.deepcopy(self.base_downtime)
        # This combo doesn't exist in the test configdb data
        downtime['site'] = 'lco'
        downtime['enclosure'] = 'domb'
        downtime['telescope'] = '2m0a'
        self.assertEqual(Downtime.objects.count(), 0)
        response = self.client.post(reverse('downtime-list'), downtime)
        self.assertEqual(Downtime.objects.count(), 0)
        self.assertIn('The site, enclosure, telescope, and instrument_type combination does not exist in Configdb', str(response.content))

    def test_post_downtime_fails_invalid_instrument_type_combo(self):
        downtime = copy.deepcopy(self.base_downtime)
        # This combo doesn't exist in the test configdb data
        downtime['site'] = 'lco'
        downtime['enclosure'] = 'doma'
        downtime['telescope'] = '2m0a'
        downtime['instrument_type'] = '1M0-SCICAM-SINISTRO'
        self.assertEqual(Downtime.objects.count(), 0)
        response = self.client.post(reverse('downtime-list'), downtime)
        self.assertEqual(Downtime.objects.count(), 0)
        self.assertIn('The site, enclosure, telescope, and instrument_type combination does not exist in Configdb', str(response.content))

    def test_post_downtime_fails_if_end_before_start(self):
        downtime = copy.deepcopy(self.base_downtime)
        start = downtime['start']
        downtime['start'] = downtime['end']
        downtime['end'] = start
        self.assertEqual(Downtime.objects.count(), 0)
        response = self.client.post(reverse('downtime-list'), downtime)
        self.assertEqual(Downtime.objects.count(), 0)
        self.assertIn('End time must be after start time', str(response.content))


class TestUptimeSerializer(TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.base_downtime = {
            'start': '2020-10-1T00:00:00Z',
            'end': '2020-10-30T00:00:00Z',
            'site': 'tst',
            'enclosure': 'doma',
            'telescope': '1m0a'
        }
        self.admin_user = User.objects.create_superuser('admin', 'admin@example.com', 'admin')
        self.client.force_login(self.admin_user)
        mock_semester = {
            'start': datetime(2020, 1, 1, tzinfo=dt_timezone.utc),
            'end': datetime(2020, 12, 31, tzinfo=dt_timezone.utc),
        }
        patcher = patch('schedule.uptime.get_semesters', return_value=[mock_semester])
        patcher.start()
        self.addCleanup(patcher.stop)

    @staticmethod
    def _make_uptime_group(uptimes, instrument_type='1M0-SCICAM-SINISTRO', site='tst',
                           enclosure='doma', telescope='1m0a', reason='Test uptime'):
        """Build one uptime group dict for the /api/uptime/ POST payload."""
        return {
            'site': site,
            'enclosure': enclosure,
            'telescope': telescope,
            'instrument_type': instrument_type,
            'reason': reason,
            'uptimes': uptimes,
        }

    def test_post_uptime(self):
        # Test POSTing to the /api/uptime/ endpoint with 3 days of uptime to add
        # Show it creates downtime for the rest of the semester that starts empty,
        # i.e. using uptime assumes non-uptime is downtime in a new semester
        data = [self._make_uptime_group([
            {'day': '2020-10-10'},
            {'day': '2020-10-11'},
            {'day': '2020-10-12'},
        ])]
        self.assertEqual(Downtime.objects.count(), 0)
        response = self.client.post(reverse('uptime'), json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 200)

        # The 3 uptime nights plus the semester bounds should produce 4 downtime periods:
        # [semester start -> evening Oct 10], [morning Oct 11 -> evening Oct 11],
        # [morning Oct 12 -> evening Oct 12], [morning Oct 13 -> semester end]
        downtimes = list(Downtime.objects.order_by('start'))
        self.assertEqual(len(downtimes), 4)

        # First downtime spans from semester start to the evening the first uptime night begins
        self.assertEqual(downtimes[0].start, datetime(2020, 1, 1, tzinfo=dt_timezone.utc))
        self.assertEqual(downtimes[0].end.date(), date(2020, 10, 10))

        # Middle two downtimes cover the daytime gaps between the three consecutive nights
        self.assertEqual(downtimes[1].start.date(), date(2020, 10, 11))
        self.assertEqual(downtimes[1].end.date(), date(2020, 10, 11))

        self.assertEqual(downtimes[2].start.date(), date(2020, 10, 12))
        self.assertEqual(downtimes[2].end.date(), date(2020, 10, 12))

        # Last downtime spans from the morning after the last uptime night to semester end
        self.assertEqual(downtimes[3].start.date(), date(2020, 10, 13))
        self.assertEqual(downtimes[3].end, datetime(2020, 12, 31, tzinfo=dt_timezone.utc))

    def test_post_downtime_merges_into_existing_downtime(self):
        # Start with a single downtime spanning the whole semester on the resource
        Downtime.objects.create(
            start=datetime(2020, 1, 1, tzinfo=dt_timezone.utc),
            end=datetime(2020, 12, 31, tzinfo=dt_timezone.utc),
            site='tst',
            enclosure='doma',
            telescope='1m0a',
            instrument_type='1M0-SCICAM-SINISTRO',
            reason='Semester downtime'
        )
        self.assertEqual(Downtime.objects.count(), 1)

        # Add 2 nights of uptime, carving them out of the semester-wide downtime
        data = [self._make_uptime_group([
            {'day': '2020-10-10'},
            {'day': '2020-10-11'},
        ])]
        response = self.client.post(reverse('uptime'), json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 200)

        # The 2 uptime nights carved out of the semester-wide downtime should produce 3 downtime periods:
        # [semester start -> evening Oct 10], [morning Oct 11 -> evening Oct 11], [morning Oct 12 -> semester end]
        downtimes = list(Downtime.objects.order_by('start'))
        self.assertEqual(len(downtimes), 3)

        # First downtime spans from semester start to the evening the first uptime night begins
        self.assertEqual(downtimes[0].start, datetime(2020, 1, 1, tzinfo=dt_timezone.utc))
        self.assertEqual(downtimes[0].end.date(), date(2020, 10, 10))

        # Middle downtime covers the daytime gap between the two consecutive nights
        self.assertEqual(downtimes[1].start.date(), date(2020, 10, 11))
        self.assertEqual(downtimes[1].end.date(), date(2020, 10, 11))

        # Last downtime spans from the morning after the last uptime night to semester end
        self.assertEqual(downtimes[2].start.date(), date(2020, 10, 12))
        self.assertEqual(downtimes[2].end, datetime(2020, 12, 31, tzinfo=dt_timezone.utc))

    def test_remove_flag_removes_uptime_day(self):
        # Add Oct 10 as an uptime day, producing 2 downtime periods
        response = self.client.post(
            reverse('uptime'),
            json.dumps([self._make_uptime_group([{'day': '2020-10-10'}])]),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Downtime.objects.count(), 2)

        # Remove Oct 10 using the remove flag
        response = self.client.post(
            reverse('uptime'),
            json.dumps([self._make_uptime_group([{'day': '2020-10-10', 'remove': True}])]),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)

        # Should collapse back to a single downtime spanning the full semester
        downtimes = list(Downtime.objects.order_by('start'))
        self.assertEqual(len(downtimes), 1)
        self.assertEqual(downtimes[0].start, datetime(2020, 1, 1, tzinfo=dt_timezone.utc))
        self.assertEqual(downtimes[0].end, datetime(2020, 12, 31, tzinfo=dt_timezone.utc))

    def test_portion_of_night_first_half_plus_second_half_equals_all(self):
        # Add Oct 10 as first_half + second_half in a single request
        data_halves = [self._make_uptime_group([
            {'day': '2020-10-10', 'portion_of_night': 'first_half'},
            {'day': '2020-10-10', 'portion_of_night': 'second_half'},
        ])]
        response = self.client.post(reverse('uptime'), json.dumps(data_halves), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        downtimes_halves = list(Downtime.objects.order_by('start'))
        self.assertEqual(len(downtimes_halves), 2)
        halves_night_start = downtimes_halves[0].end
        halves_night_end = downtimes_halves[1].start

        # Reset and add Oct 10 as a full night using 'all'
        Downtime.objects.all().delete()
        data_all = [self._make_uptime_group([{'day': '2020-10-10', 'portion_of_night': 'all'}])]
        response = self.client.post(reverse('uptime'), json.dumps(data_all), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        downtimes_all = list(Downtime.objects.order_by('start'))
        self.assertEqual(len(downtimes_all), 2)

        # The night window boundaries must be identical
        self.assertEqual(downtimes_all[0].end, halves_night_start)
        self.assertEqual(downtimes_all[1].start, halves_night_end)

    def test_late_start_enlarges_pre_night_downtime(self):
        # Add Oct 10 with default late_start=0 and record when the uptime window begins
        self.client.post(
            reverse('uptime'),
            json.dumps([self._make_uptime_group([{'day': '2020-10-10'}])]),
            content_type='application/json'
        )
        normal_night_start = Downtime.objects.order_by('start').first().end

        # Reset and add Oct 10 with late_start=60 minutes
        Downtime.objects.all().delete()
        self.client.post(
            reverse('uptime'),
            json.dumps([self._make_uptime_group([{'day': '2020-10-10', 'late_start': 60}])]),
            content_type='application/json'
        )
        late_night_start = Downtime.objects.order_by('start').first().end

        # The pre-night downtime should end exactly 60 minutes later
        self.assertEqual(late_night_start - normal_night_start, timedelta(minutes=60))

    def test_early_end_enlarges_post_night_downtime(self):
        # Add Oct 10 with default early_end=0 and record when the uptime window ends
        self.client.post(
            reverse('uptime'),
            json.dumps([self._make_uptime_group([{'day': '2020-10-10'}])]),
            content_type='application/json'
        )
        normal_night_end = list(Downtime.objects.order_by('start'))[1].start

        # Reset and add Oct 10 with early_end=60 minutes
        Downtime.objects.all().delete()
        self.client.post(
            reverse('uptime'),
            json.dumps([self._make_uptime_group([{'day': '2020-10-10', 'early_end': 60}])]),
            content_type='application/json'
        )
        early_night_end = list(Downtime.objects.order_by('start'))[1].start

        # The post-night downtime should start exactly 60 minutes earlier
        self.assertEqual(normal_night_end - early_night_end, timedelta(minutes=60))

    def test_multiple_instrument_types_on_same_telescope(self):
        # POST a single request with uptime entries for two instrument types on tst/doma/1m0a
        data = [
            self._make_uptime_group([{'day': '2020-10-10'}]),
            self._make_uptime_group([{'day': '2020-10-10'}], instrument_type='1M0-SCICAM-SBIG'),
        ]
        self.assertEqual(Downtime.objects.count(), 0)
        response = self.client.post(reverse('uptime'), json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 200)

        # Each instrument type should produce its own independent set of 2 downtime periods
        # (semester start -> night start, night end -> semester end)
        self.assertEqual(Downtime.objects.count(), 4)
        self.assertEqual(Downtime.objects.filter(instrument_type='1M0-SCICAM-SINISTRO').count(), 2)
        self.assertEqual(Downtime.objects.filter(instrument_type='1M0-SCICAM-SBIG').count(), 2)

        # Both instrument types should produce identical downtime boundaries since they share
        # the same telescope and uptime dates
        sinistro_downtimes = list(Downtime.objects.filter(instrument_type='1M0-SCICAM-SINISTRO').order_by('start'))
        sbig_downtimes = list(Downtime.objects.filter(instrument_type='1M0-SCICAM-SBIG').order_by('start'))
        self.assertEqual(sinistro_downtimes[0].start, sbig_downtimes[0].start)
        self.assertEqual(sinistro_downtimes[0].end, sbig_downtimes[0].end)
        self.assertEqual(sinistro_downtimes[1].start, sbig_downtimes[1].start)
        self.assertEqual(sinistro_downtimes[1].end, sbig_downtimes[1].end)

    def test_get_uptime_matches_posted_uptime_nights(self):
        # Create 3 consecutive uptime nights via POST
        post_data = [self._make_uptime_group([
            {'day': '2020-10-10'},
            {'day': '2020-10-11'},
            {'day': '2020-10-12'},
        ])]
        post_response = self.client.post(reverse('uptime'), json.dumps(post_data), content_type='application/json')
        self.assertEqual(post_response.status_code, 200)

        # GET the uptime endpoint filtered to the date range spanning those 3 nights
        get_response = self.client.get(reverse('uptime'), {
            'site': 'tst',
            'enclosure': 'doma',
            'telescope': '1m0a',
            'instrument_type': '1M0-SCICAM-SINISTRO',
            'start': '2020-10-10T00:00:00Z',
            'end': '2020-10-13T12:00:00Z',
        })
        self.assertEqual(get_response.status_code, 200)

        # Should get back exactly 3 uptime intervals, one per posted night
        uptimes = get_response.json()['uptimes']
        self.assertEqual(len(uptimes), 3)

        # Each interval should start on the correct night's date and span several hours
        expected_dates = [date(2020, 10, 10), date(2020, 10, 11), date(2020, 10, 12)]
        for (start_str, end_str), expected_date in zip(uptimes, expected_dates):
            uptime_start = datetime.fromisoformat(start_str.replace('Z', '+00:00'))
            uptime_end = datetime.fromisoformat(end_str.replace('Z', '+00:00'))
            self.assertEqual(uptime_start.date(), expected_date)
            self.assertGreater(uptime_end - uptime_start, timedelta(hours=4))

    def test_remove_second_half_uptime_with_all(self):
        # Query range covers the full Oct 10 night (22:00 UTC Oct 10 -> ~04:00 UTC Oct 11)
        get_params = {
            'site': 'tst', 'enclosure': 'doma', 'telescope': '1m0a',
            'instrument_type': '1M0-SCICAM-SINISTRO',
            'start': '2020-01-01T00:00:00Z',
            'end': '2020-12-31T00:00:00Z',
        }

        # POST second_half of Oct 10 as an uptime
        post_response = self.client.post(
            reverse('uptime'),
            json.dumps([self._make_uptime_group([{'day': '2020-10-10', 'portion_of_night': 'second_half'}])]),
            content_type='application/json'
        )
        self.assertEqual(post_response.status_code, 200)

        # GET and verify that an uptime was created
        get_response = self.client.get(reverse('uptime'), get_params)
        self.assertEqual(get_response.status_code, 200)
        uptimes = get_response.json()['uptimes']
        self.assertEqual(len(uptimes), 1)

        # POST remove=True with portion_of_night=all to remove the entire Oct 10 night
        remove_response = self.client.post(
            reverse('uptime'),
            json.dumps([self._make_uptime_group([{'day': '2020-10-10', 'remove': True, 'portion_of_night': 'all'}])]),
            content_type='application/json'
        )
        self.assertEqual(remove_response.status_code, 200)

        # GET again — the full night was removed so no uptimes should remain for this window
        get_response = self.client.get(reverse('uptime'), get_params)
        self.assertEqual(get_response.status_code, 200)
        self.assertEqual(get_response.json()['uptimes'], [])

    def test_post_uptime_fails_invalid_instrument_type(self):
        # 'INVALID' is not a recognised instrument type in configdb
        data = [self._make_uptime_group([{'day': '2020-10-10'}], instrument_type='INVALID')]
        response = self.client.post(reverse('uptime'), json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        # Errors are wrapped in a list because UptimesSerializer uses many=True
        error = response.json()[0]
        self.assertIn('instrument_type', error)
        self.assertIn('"INVALID" is not a valid choice', error['instrument_type'][0])
        self.assertEqual(Downtime.objects.count(), 0)

    def test_post_uptime_fails_invalid_site_enclosure_telescope_instrument_type_combo(self):
        # 2M0-SCICAM-MUSCAT is a valid instrument type but only exists on tst/doma/2m0a,
        # not on tst/doma/1m0a — so this combination fails cross-field validation
        data = [self._make_uptime_group([{'day': '2020-10-10'}], instrument_type='2M0-SCICAM-MUSCAT')]
        response = self.client.post(reverse('uptime'), json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('tst.doma.1m0a.2M0-SCICAM-MUSCAT does not exist in Configdb', str(response.content))
        self.assertEqual(Downtime.objects.count(), 0)

    def test_post_uptime_fails_when_get_semesters_raises(self):
        from schedule.uptime import UptimeException
        data = [self._make_uptime_group([{'day': '2020-10-10'}])]
        with patch('schedule.uptime.get_semesters', side_effect=UptimeException('Observation portal unavailable')):
            response = self.client.post(reverse('uptime'), json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('Observation portal unavailable', response.json()['error'])
        self.assertEqual(Downtime.objects.count(), 0)
