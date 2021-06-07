from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _
from rest_framework.schemas.openapi import AutoSchema

from schedule.configdb import configdb


class Downtime(models.Model):
    schema=AutoSchema(tags=['Downtime'])
    start = models.DateTimeField()
    end = models.DateTimeField()
    site = models.CharField(max_length=3,
        help_text='3 character site code to apply downtime on'
    )
    enclosure = models.CharField(max_length=4,
        help_text='4 character enclosure code to apply downtime on, i.e. doma'
    )
    telescope = models.CharField(max_length=4,
        help_text='4 character telescope code to apply downtime on, i.e. 1m0a'
    )
    instrument_type = models.CharField(max_length=255, default='', blank=True,
        help_text='The instrument type in configuration db. If specified, downtime will only apply on this instrument type'
    )
    reason = models.CharField(max_length=3000, default='', blank=True,
        help_text='A descriptive reason for why this downtime exists'
    )
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('start',)

    def as_dict(self):
        return {
            'start': self.start,
            'end': self.end,
            'site': self.site,
            'enclosure': self.enclosure,
            'telescope': self.telescope,
            'instrument_type': self.instrument_type,
            'reason': self.reason
        }

    def clean(self, *args, **kwargs):
        if self.start >= self.end:
            raise ValidationError(_('End time must be after start time'))

        if not configdb.instrument_exists(self.site, self.enclosure, self.telescope, self.instrument_type):
            raise ValidationError(_('The site, enclosure, telescope, and instrument_type combination does not exist in Configdb'))
