from rest_framework import serializers
from django.utils.translation import gettext as _

from schedule.models import Downtime
from schedule.configdb import configdb


class DowntimeSerializer(serializers.ModelSerializer):
    start = serializers.DateTimeField(help_text='Start date/time in `%Y-%m-%dT%H:%M:%S` format')
    end = serializers.DateTimeField(help_text='End date/time in `%Y-%m-%dT%H:%M:%S` format')
    site = serializers.ChoiceField(choices=configdb.get_site_tuples(), required=True,
                                   help_text='Site code to apply downtime on')
    enclosure = serializers.ChoiceField(choices=configdb.get_enclosure_tuples(), required=True,
                                        help_text='Enclosure code to apply downtime on')
    telescope = serializers.ChoiceField(choices=configdb.get_telescope_tuples(), required=True,
                                        help_text='Telescope code to apply downtime on')
    instrument_type = serializers.ChoiceField(choices=configdb.get_instrument_type_tuples(include_blank=True), required=False,
                                              help_text='Instrument type to apply downtime on')

    class Meta:
        model = Downtime
        fields = ('id', 'start', 'end', 'site', 'enclosure', 'telescope', 'instrument_type', 'reason')

    def validate(self, data):
        if data['end'] <= data['start']:
            raise serializers.ValidationError(_("End time must be after start time"))

        if not configdb.instrument_exists(data['site'], data['enclosure'], data['telescope'], data.get('instrument_type', '')):
            raise serializers.ValidationError(_('The site, enclosure, telescope, and instrument_type combination does not exist in Configdb'))

        return super().validate(data)


class UptimeSerializer(serializers.Serializer):
    day = serializers.DateField(help_text='Start date in `%Y-%m-%d` format', required=True)
    remove = serializers.BooleanField(help_text='If true, remove this day from the uptime calendar, otherwise add it', default=False, required=False)
    portion_of_night = serializers.ChoiceField(choices=[('all', 'all'), ('first_half', 'first_half'), ('second_half', 'second_half')], default='all', required=False)
    late_start = serializers.FloatField(help_text='Minutes to chop off the beginning of night', default=0, required=False)
    early_end = serializers.FloatField(help_text='Minutes to chop off the end of night', default=0, required=False)


class UptimesSerializer(serializers.Serializer):
    uptimes = UptimeSerializer(many=True)
    reason = serializers.CharField(help_text='A short description of what this downtime represents', default='Created through uptime API', required=False)
    site = serializers.ChoiceField(choices=configdb.get_site_tuples(), required=True,
                                   help_text='Site code to apply downtime on')
    enclosure = serializers.ChoiceField(choices=configdb.get_enclosure_tuples(), required=True,
                                        help_text='Enclosure code to apply downtime on')
    telescope = serializers.ChoiceField(choices=configdb.get_telescope_tuples(), required=True,
                                        help_text='Telescope code to apply downtime on')
    instrument_type = serializers.ChoiceField(choices=configdb.get_instrument_type_tuples(include_blank=False), required=False,
                                                      allow_blank=True, help_text='Instrument type to apply downtime on')

    def validate(self, data):
        instrument_type = data.get('instrument_type', '')
        if not configdb.instrument_exists(data['site'], data['enclosure'], data['telescope'], instrument_type):
            raise serializers.ValidationError(_(f'The site, enclosure, telescope, and instrument_type combination {data["site"]}.{data["enclosure"]}.{data["telescope"]}.{instrument_type} does not exist in Configdb'))

        return super().validate(data)


class GetUptimesSerializer(serializers.Serializer):
    start = serializers.DateTimeField(help_text='Start date/time in `%Y-%m-%dT%H:%M:%S` format', required=True)
    end = serializers.DateTimeField(help_text='End date/time in `%Y-%m-%dT%H:%M:%S` format', required=True)
    site = serializers.ChoiceField(choices=configdb.get_site_tuples(), required=True,
                                   help_text='Site code to apply downtime on')
    enclosure = serializers.ChoiceField(choices=configdb.get_enclosure_tuples(), required=True,
                                        help_text='Enclosure code to apply downtime on')
    telescope = serializers.ChoiceField(choices=configdb.get_telescope_tuples(), required=True,
                                        help_text='Telescope code to apply downtime on')
    instrument_type = serializers.ChoiceField(choices=configdb.get_instrument_type_tuples(include_blank=False), required=False,
                                                      allow_blank=True, help_text='Instrument type to apply downtime on')
