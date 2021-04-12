from django import forms

from schedule.configdb import configdb
from schedule.models import Downtime


class DowntimeForm(forms.ModelForm):
    class Meta:
        model = Downtime
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['site'] = forms.ChoiceField(choices=configdb.get_site_tuples(include_blank=False))
        self.fields['enclosure'] = forms.ChoiceField(choices=configdb.get_enclosure_tuples(include_blank=False))
        self.fields['telescope'] = forms.ChoiceField(choices=configdb.get_telescope_tuples(include_blank=False))
        self.fields['instrument_type'] = forms.ChoiceField(choices=configdb.get_instrument_type_tuples(include_blank=True), required=False)
