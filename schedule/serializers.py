from rest_framework import serializers
from django.utils.translation import ugettext as _

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
        fields = ('start', 'end', 'site', 'enclosure', 'telescope', 'instrument_type', 'reason')

    def validate(self, data):
        if data['end'] <= data['start']:
            raise serializers.ValidationError(_("End time must be after start time"))

        if not configdb.instrument_exists(data['site'], data['enclosure'], data['telescope'], data.get('instrument_type', '')):
            raise serializers.ValidationError(_('The site, enclosure, telescope, and instrument_type combination does not exist in Configdb'))

        return super().validate(data)
