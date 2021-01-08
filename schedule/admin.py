# -*- coding: utf-8 -*-
from django.contrib import admin

from .models import Downtime


@admin.register(Downtime)
class DowntimeAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'start',
        'end',
        'site',
        'enclosure',
        'telescope',
        'reason',
        'created',
        'modified',
    )
    list_filter = ('start', 'end', 'created', 'modified', 'site', 'enclosure', 'telescope')
