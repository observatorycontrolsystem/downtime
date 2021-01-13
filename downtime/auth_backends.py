import requests
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.backends import BaseBackend
from rest_framework import exceptions, authentication


class OAuth2Backend(BaseBackend):
    """
    Authenticate against the Oauth backend, using
    grant_type: password
    """

    def authenticate(self, request, username=None, password=None):
        response = requests.post(
            settings.OAUTH_TOKEN_URL,
            data={
                'grant_type': 'password',
                'username': username,
                'password': password,
                'client_id': settings.OAUTH_CLIENT_ID,
                'client_secret': settings.OAUTH_CLIENT_SECRET
            }
        )
        if response.status_code == 200:
            # user is authenticated, so now query the profile to figure out if the user is staff
            bearer_token = response.json()['access_token']
            response2 = requests.get(
                settings.OAUTH_PROFILE_URL,
                headers={f'Authorization': 'Bearer {bearer_token}'}
            )
            if not response2.status_code == 200:
                raise exceptions.AuthenticationFailed('Failed to access user profile')
            user, _ = User.objects.update_or_create(
                username=response2.json()['username'],
                defaults={
                    'is_superuser': response2.json()['is_staff'],
                    'is_staff': response2.json()['is_staff']
                }
            )
            return user
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None


class BearerAuthentication(authentication.BaseAuthentication):
    """
    Allows users to authenticate using the bearer token recieved from
    the observation portal auth server (or via the /api-token-auth/ endpoint).
    It is validated by attempting to request the user profile, which requires authentication
    """
    def authenticate(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if 'Bearer' not in auth_header:
            return None

        bearer = auth_header.split('Bearer')[1].strip()
        response = requests.get(
            settings.OAUTH_PROFILE_URL,
            headers={'Authorization': 'Bearer {}'.format(bearer)}
        )

        if not response.status_code == 200:
            raise exceptions.AuthenticationFailed('No Such User or Invalid Bearer Token')

        user, _ = User.objects.update_or_create(
            username=response.json()['username'],
            defaults={
                'is_superuser': response.json()['is_staff'],
                'is_staff': response.json()['is_staff']
            }
        )

        return (user, None)
