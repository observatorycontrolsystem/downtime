# -*- coding: utf-8 -*-
from django.contrib import admin

from schedule.models import Downtime
from schedule.forms import DowntimeForm


@admin.register(Downtime)
class DowntimeAdmin(admin.ModelAdmin):
    form = DowntimeForm
    list_display = (
        'id',
        'start',
        'end',
        'site',
        'enclosure',
        'telescope',
        'instrument_type',
        'reason',
        'created',
        'modified',
    )
    list_filter = ('start', 'end', 'created', 'modified', 'site', 'enclosure', 'telescope', 'instrument_type')
