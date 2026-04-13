from django_filters.views import FilterView
from django.utils import timezone
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework import status

from schedule.models import Downtime
from schedule.filters import DowntimeFilter
from schedule.serializers import UptimesSerializer, GetUptimesSerializer
from schedule.uptime import modify_schedule_with_uptimes, convert_downtimes_to_uptimes, UptimeException

class DowntimeListView(FilterView):
    model = Downtime
    filterset_class = DowntimeFilter
    paginate_by = 50
    template_name = 'downtime_list.html'

    def get_queryset(self):
        return Downtime.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['logo_url'] = settings.LOGO_URL
        return context

    def get_filterset_kwargs(self, filterset_class):
        kwargs = super(DowntimeListView, self).get_filterset_kwargs(filterset_class)
        # If there are no query parameters or the only query parameter is for pagination, default to
        # filtering out downtimes in the past
        if kwargs['data'] is None or (len(kwargs['data']) == 1 and 'page' in kwargs['data']):
            kwargs['data'] = {
                'ends_after': timezone.now()
            }
        return kwargs


class UptimeView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, format=None):
        serializer = UptimesSerializer(data=request.data, many=True)

        if serializer.is_valid():
            try:
                modify_schedule_with_uptimes(serializer.validated_data)
            except UptimeException as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
            return Response({'success': True})
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, format=None):
        serializer = GetUptimesSerializer(data=request.query_params.dict())
        if serializer.is_valid():
            # Use the query params to get the Downtimes associated
            params = serializer.validated_data
            downtimes = Downtime.objects.filter(end__gte=params['start'], start__lte=params['end'],
                                                site=params['site'], enclosure=params['enclosure'],
                                                telescope=params['telescope'],
                                                instrument_type=params['instrument_type'])
            if params.get('reason'):
                downtimes = downtimes.filter(reason__icontains=params['reason'])

            uptimes = convert_downtimes_to_uptimes(downtimes, params['start'], params['end'])
            response = params
            # Filter out things outside the bounds, which are reported incorrects in the interval as (high, low)
            response['uptimes'] = [uptime for uptime in uptimes.toTupleList() if uptime[0] < uptime[1]]
            return Response(response)

        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
