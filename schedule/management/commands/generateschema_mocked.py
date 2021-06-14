import os
import json

from rest_framework.management.commands.generateschema import Command as GenerateSchemaCommand
from django.conf import settings
import responses

CONFIGDB_TEST_FILE = os.path.join(settings.BASE_DIR, 'downtime/test_data/configdb.json')


class Command(GenerateSchemaCommand):
    help = "Command to generate OpenAPI schema with external services mocked"
    def __init__(self):
        super().__init__()
        # Mock out ConfigDB response for doc generation.
        # TODO: Add mock ConfigDB dataset for docs across all projects
        responses._default_mock.__enter__()
        responses.add(
            responses.GET, settings.CONFIGDB_URL + '/sites/', match_querystring=True,
            json=json.loads(open(CONFIGDB_TEST_FILE).read()), status=200
        )

    def handle(self, *args, **options):
        super().handle(*args, **options)
