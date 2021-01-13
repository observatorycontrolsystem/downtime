import requests
from django.core.cache import caches
from django.utils.translation import ugettext as _
from django.conf import settings


class ConfigDBException(Exception):
    """Raise on error retrieving or processing configuration data."""
    pass


class ConfigDB(object):
    """Class to retrieve and process configuration data."""

    @staticmethod
    def _get_configdb_data(resource: str):
        """
        Return all configuration data.

        Return all data from ConfigDB at the given endpoint. Check first if the data is already cached, and
        if so, return that.

        Parameters:
            resource: ConfigDB endpoint
        Returns:
            Data retrieved
        """
        error_message = _((
            'ConfigDB connection is currently down, please wait a few minutes and try again. If this problem '
            'persists then please contact support.'
        ))
        data = caches['locmem'].get(resource)
        if not data:
            try:
                r = requests.get(settings.CONFIGDB_URL + f'/{resource}/')
                r.raise_for_status()
            except (requests.exceptions.RequestException, requests.exceptions.HTTPError) as e:
                msg = f'{e.__class__.__name__}: {error_message}'
                raise ConfigDBException(msg)
            try:
                data = r.json()['results']
            except KeyError:
                raise ConfigDBException(error_message)
            # Cache the results for 15 minutes.
            caches['locmem'].set(resource, data, 900)
        return data

    def get_site_data(self):
        """Return ConfigDB sites data."""
        return self._get_configdb_data('sites')

    def get_site_tuples(self, include_blank=False):
        site_data = self.get_site_data()
        sites = [(site['code'], site['code']) for site in site_data]
        if include_blank:
            sites.append(('', ''))
        return sites

    def get_enclosure_tuples(self, include_blank=False):
        enclosure_set = set()
        site_data = self.get_site_data()
        for site in site_data:
            for enclosure in site['enclosure_set']:
                enclosure_set.add(enclosure['code'])

        enclosures = [(enclosure, enclosure) for enclosure in enclosure_set]
        if include_blank:
            enclosures.append(('', ''))
        return enclosures

    def get_telescope_tuples(self, include_blank=False):
        telescope_set = set()
        site_data = self.get_site_data()
        for site in site_data:
            for enclosure in site['enclosure_set']:
                for telescope in enclosure['telescope_set']:
                    telescope_set.add(telescope['code'])

        telescopes = [(telescope, telescope) for telescope in telescope_set]
        if include_blank:
            telescopes.append(('', ''))
        return telescopes

    def telescope_exists(self, site_code, enclosure_code, telescope_code):
        site_data = self.get_site_data()
        for site in site_data:
            if site_code == site['code']:
                for enclosure in site['enclosure_set']:
                    if enclosure_code == enclosure['code']:
                        for telescope in enclosure['telescope_set']:
                            if telescope_code == telescope['code']:
                                return True
        return False


configdb = ConfigDB()
