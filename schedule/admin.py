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
        'observatory',
        'telescope',
        'reason',
        'created',
        'updated',
    )
    list_filter = ('start', 'end', 'created', 'updated', 'site', 'observatory', 'telescope')
