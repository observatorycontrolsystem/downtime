import django_filters

from schedule.configdb import configdb
from schedule.models import Downtime


class DowntimeFilter(django_filters.FilterSet):
    starts_after = django_filters.DateTimeFilter(field_name='start', lookup_expr='gte', label='Starts after')
    starts_before = django_filters.DateTimeFilter(field_name='start', lookup_expr='lte', label='Starts before')
    ends_after = django_filters.DateTimeFilter(field_name='end', lookup_expr='gte', label='Ends after')
    ends_before = django_filters.DateTimeFilter(field_name='end', lookup_expr='lte', label='Ends before')
    site = django_filters.MultipleChoiceFilter(field_name='site', choices=sorted(configdb.get_site_tuples()))
    enclosure = django_filters.MultipleChoiceFilter(field_name='enclosure', choices=sorted(configdb.get_enclosure_tuples()))
    telescope = django_filters.MultipleChoiceFilter(field_name='telescope', choices=sorted(configdb.get_telescope_tuples()))
    reason = django_filters.CharFilter(field_name='reason', lookup_expr='icontains', label='Reason contains')
    created_after = django_filters.DateTimeFilter(field_name='created', lookup_expr='gte', label='Created After')
    created_before = django_filters.DateTimeFilter(field_name='created', lookup_expr='lte', label='Created Before')
    modified_after = django_filters.DateTimeFilter(field_name='modified', lookup_expr='gte', label='Modified After')
    modified_before = django_filters.DateTimeFilter(field_name='modified', lookup_expr='lte', label='Modified Before')
    order = django_filters.OrderingFilter(
        fields=(
            ('start', 'start'),
            ('end', 'end'),
            ('modified', 'modified'),
            ('created', 'created'),
        )
    )

    class Meta:
        model = Downtime
        fields = (
            'starts_before', 'starts_after', 'ends_before', 'ends_after', 'site', 'enclosure', 'telescope',
            'reason', 'created_after', 'created_before', 'modified_after', 'modified_before'
        )
