from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend

from schedule.serializers import DowntimeSerializer
from schedule.models import Downtime
from schedule.filters import DowntimeFilter


class DowntimeViewSet(viewsets.ModelViewSet):
    queryset = Downtime.objects.all()
    serializer_class = DowntimeSerializer
    filter_class = DowntimeFilter
    filter_backends = (
        filters.OrderingFilter,
        DjangoFilterBackend
    )
    ordering = ('created',)
