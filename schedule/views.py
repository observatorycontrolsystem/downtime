from django_filters.views import FilterView
from django.utils import timezone
from django.conf import settings

from schedule.models import Downtime
from schedule.filters import DowntimeFilter


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
