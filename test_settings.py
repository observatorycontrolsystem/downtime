from downtime.settings import *  # noqa

# Need a valid url to run tests even though it is mocked
CONFIGDB_URL = os.getenv('CONFIGDB_URL', 'http://configdb-dev')

