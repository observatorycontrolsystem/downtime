from datetime import timedelta

from django.test import TestCase
from django.utils import timezone
from django.urls import reverse
from django.contrib.auth.models import User

from schedule.models import Downtime


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
            'observatory': 'domx',
            'telescope': '1m0z',
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
        self.assertIn('Start time must come before end time', str(response.content))
