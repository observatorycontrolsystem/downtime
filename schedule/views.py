import django_filters
from django.http import JsonResponse
from django.views import View

from schedule.models import Downtime


class DowntimeFilter(django_filters.FilterSet):
    reason = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Downtime
        fields = {
            'start': ['lt', 'gt'],
            'end': ['lt', 'gt'],
            'site': ['exact'],
            'observatory': ['exact'],
            'telescope': ['exact'],
        }


class DowntimeView(View):
    def get(self, request):
        f = DowntimeFilter(request.GET, queryset=Downtime.objects.all())
        return JsonResponse([dt.as_dict() for dt in f.qs.all()], safe=False)
