from datetime import timedelta
import copy

from django.test import TestCase
from django.utils import timezone
from django.urls import reverse
from django.contrib.auth.models import User

from schedule.models import Downtime
from schedule.serializers import DowntimeSerializer


class TestModelAdmin(TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.admin_user = User.objects.create_superuser('admin', 'admin@example.com', 'admin')
        self.client.force_login(self.admin_user)

    @staticmethod
    def _get_post_data_for_new_downtime(start, end):
        return {
            'reason': 'Maintenance',
            'site': 'tst',
            'enclosure': 'domx',
            'telescope': '1m0z',
            # POST data to the model admin add view expect that model fields that are
            # DateTimeFields are separated by date and time as follows
            'start_0': start.date(),
            'start_1': start.time(),
            'end_0': end.date(),
            'end_1': end.time(),
        }

    def test_add_downtime(self):
        start = timezone.now() - timedelta(days=2)
        end = start + timedelta(hours=1)
        data = self._get_post_data_for_new_downtime(start, end)
        self.assertEqual(Downtime.objects.count(), 0)
        self.client.post(reverse('admin:schedule_downtime_add'), data, follow=True)
        self.assertEqual(Downtime.objects.count(), 1)

    def test_downtime_with_end_before_start_not_allowed(self):
        start = timezone.now() - timedelta(days=2)
        end = start - timedelta(hours=1)
        data = self._get_post_data_for_new_downtime(start, end)
        self.assertEqual(Downtime.objects.count(), 0)
        response = self.client.post(reverse('admin:schedule_downtime_add'), data, follow=True)
        self.assertEqual(Downtime.objects.count(), 0)
        self.assertIn('End time must be after start time', str(response.content))


class TestDowntimeSerializer(TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.base_downtime = {
            'start': '2020-10-10T20:10:10Z',
            'end': '2020-10-10T21:22:22Z',
            'site': 'tst',
            'enclosure': 'doma',
            'telescope': '1m0a'
        }
        self.admin_user = User.objects.create_superuser('admin', 'admin@example.com', 'admin')
        self.client.force_login(self.admin_user)

    def test_post_downtime(self):
        downtime = copy.deepcopy(self.base_downtime)
        self.assertEqual(Downtime.objects.count(), 0)
        response = self.client.post(reverse('downtime-list'), downtime)
        self.assertEqual(Downtime.objects.count(), 1)

    def test_post_downtime_fails_if_not_logged_in(self):
        self.client.logout()
        downtime = copy.deepcopy(self.base_downtime)
        self.assertEqual(Downtime.objects.count(), 0)
        response = self.client.post(reverse('downtime-list'), downtime)
        self.assertEqual(Downtime.objects.count(), 0)

    def test_post_downtime_fails_invalid_site(self):
        downtime = copy.deepcopy(self.base_downtime)
        downtime['site'] = 'nop' # this site doesnt exist in the test configdb data
        self.assertEqual(Downtime.objects.count(), 0)
        response = self.client.post(reverse('downtime-list'), downtime)
        self.assertEqual(Downtime.objects.count(), 0)
        self.assertIn('site', response.json())
        self.assertIn('"nop" is not a valid choice', response.json()['site'][0])

    def test_post_downtime_fails_invalid_telescope_combo(self):
        downtime = copy.deepcopy(self.base_downtime)
        # This combo doesn't exist in the test configdb data
        downtime['site'] = 'lco'
        downtime['enclosure'] = 'domb'
        downtime['telescope'] = '2m0a'
        self.assertEqual(Downtime.objects.count(), 0)
        response = self.client.post(reverse('downtime-list'), downtime)
        self.assertEqual(Downtime.objects.count(), 0)
        self.assertIn('The site, enclosure, and telescope combination does not exist in Configdb', str(response.content))

    def test_post_downtime_fails_if_end_before_start(self):
        downtime = copy.deepcopy(self.base_downtime)
        start = downtime['start']
        downtime['start'] = downtime['end']
        downtime['end'] = start
        self.assertEqual(Downtime.objects.count(), 0)
        response = self.client.post(reverse('downtime-list'), downtime)
        self.assertEqual(Downtime.objects.count(), 0)
        self.assertIn('End time must be after start time', str(response.content))
