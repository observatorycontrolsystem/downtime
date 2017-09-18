from django.db import models
from django.core.exceptions import ValidationError


class Downtime(models.Model):
    start = models.DateTimeField()
    end = models.DateTimeField()
    site = models.CharField(max_length=3)
    observatory = models.CharField(max_length=4)
    telescope = models.CharField(max_length=4)
    reason = models.CharField(max_length=3000, default='', blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('start',)

    def as_dict(self):
        return {
            'start': self.start,
            'end': self.end,
            'site': self.site,
            'observatory': self.observatory,
            'telescope': self.telescope,
            'reason': self.reason
        }

    def clean(self, *args, **kwargs):
        if self.start >= self.end:
            raise ValidationError('Start time must come before end time')
