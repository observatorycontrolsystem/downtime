import warnings

from django_filters.rest_framework import DjangoFilterBackend


class SchemaDjangoFilterBackend(DjangoFilterBackend):
    """A DjangoFilterBackend that still advertises its filters to DRF's OpenAPI generator.

    django-filter removed its built-in schema generation in 25.1 in favour of drf-spectacular,
    which would drop every filter query parameter from our published API reference. This keeps
    the original implementation so the generated schema is unchanged.
    """

    def get_schema_operation_parameters(self, view):
        try:
            queryset = view.get_queryset()
        except Exception:
            queryset = None
            warnings.warn('{} is not compatible with schema generation'.format(view.__class__))

        filterset_class = self.get_filterset_class(view, queryset)

        if not filterset_class:
            return []

        parameters = []
        for field_name, field in filterset_class.base_filters.items():
            parameter = {
                'name': field_name,
                'required': field.extra['required'],
                'in': 'query',
                'description': field.label if field.label is not None else field_name,
                'schema': {
                    'type': 'string',
                },
            }
            if field.extra and 'choices' in field.extra:
                parameter['schema']['enum'] = [c[0] for c in field.extra['choices']]
            parameters.append(parameter)
        return parameters
