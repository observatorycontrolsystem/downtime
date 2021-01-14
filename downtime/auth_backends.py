import requests
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.backends import BaseBackend
from rest_framework import exceptions


class OAuth2Backend(BaseBackend):
    """
    Authenticate against the Oauth backend, using
    grant_type: password
    """

    def authenticate(self, request, username=None, password=None):
        token_response = requests.post(
            settings.OAUTH_TOKEN_URL,
            data={
                'grant_type': 'password',
                'username': username,
                'password': password,
                'client_id': settings.OAUTH_CLIENT_ID,
                'client_secret': settings.OAUTH_CLIENT_SECRET
            }
        )
        if token_response.status_code == 200:
            # user is authenticated, so now query the profile to figure out if the user is staff
            bearer_token = token_response.json()['access_token']
            profile_response = requests.get(
                settings.OAUTH_PROFILE_URL,
                headers={'Authorization': f'Bearer {bearer_token}'}
            )
            if not profile_response.status_code == 200:
                raise exceptions.AuthenticationFailed('Failed to access user profile')
            user, _ = User.objects.update_or_create(
                username=profile_response.json()['username'],
                defaults={
                    'is_superuser': profile_response.json()['is_staff'],
                    'is_staff': profile_response.json()['is_staff']
                }
            )
            return user
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
