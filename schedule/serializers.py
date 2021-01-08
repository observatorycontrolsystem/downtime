from rest_framework import serializers

from schedule.models import Downtime
from schedule.configdb import configdb


class DowntimeSerializer(serializers.ModelSerializer):
    site = serializers.ChoiceField(choices=configdb.get_site_tuples(), required=True)
    enclosure = serializers.ChoiceField(choices=configdb.get_enclosure_tuples(), required=True)
    telescope = serializers.ChoiceField(choices=configdb.get_telescope_tuples(), required=True)

    class Meta:
        model = Downtime
        fields = ('start', 'end', 'site', 'enclosure', 'telescope', 'reason')

