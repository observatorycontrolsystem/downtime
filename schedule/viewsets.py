from rest_framework import viewsets, filters

from schedule.serializers import DowntimeSerializer
from schedule.models import Downtime
from schedule.filters import DowntimeFilter
from schedule.filter_backends import SchemaDjangoFilterBackend


class DowntimeViewSet(viewsets.ModelViewSet):
    queryset = Downtime.objects.all()
    http_method_names = ['get', 'post', 'delete', 'head', 'options']
    serializer_class = DowntimeSerializer
    filterset_class = DowntimeFilter
    filter_backends = (
        filters.OrderingFilter,
        SchemaDjangoFilterBackend
    )
    ordering = ('created',)
