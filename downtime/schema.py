from rest_framework.schemas.openapi import SchemaGenerator

class DowntimeSchemaGenerator(SchemaGenerator):
    def get_schema(self, *args, **kwargs):
        schema = super().get_schema(*args, **kwargs)
        schema['info']['title'] = 'Downtime Database'
        schema['info']['description'] = 'An application with a database that stores periods of scheduled telescope downtime for an observatory with an API to access those downtimes.'
        schema['info']['version'] = 'latest'
        return schema
