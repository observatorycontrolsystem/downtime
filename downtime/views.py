import requests
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.http import HttpResponseBadRequest


class BearerTokenView(APIView):
    ''' This endpoint takes the observation portal username/password in its data and returns a bearer token 
        that can be used for future API calls to post downtimes.
    '''
    permission_classes = [AllowAny]
    def post(self, request, *args, **kwargs):
        if 'username' not in request.data or 'password' not in request.data:
            return HttpResponseBadRequest("Must include username and password to get bearer token")
        response = requests.post(
            settings.OAUTH_TOKEN_URL,
            data={
                'grant_type': 'password',
                'username': request.data['username'],
                'password': request.data['password'],
                'client_id': settings.OAUTH_CLIENT_ID,
                'client_secret': settings.OAUTH_CLIENT_SECRET
            }
        )
        if response.status_code == 200:
            bearer_token = response.json()['access_token']
            return Response({'bearer_token': bearer_token})
        else:
            return HttpResponseBadRequest(response.json())
