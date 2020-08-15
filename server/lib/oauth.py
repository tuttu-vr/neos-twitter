import os
from logging import getLogger
from requests_oauthlib import OAuth1Session
from urllib.parse import parse_qsl

logger = getLogger(__name__)


CONSUMER_KEY = os.getenv('TWITTER_CONSUMER_KEY', '')
CONSUMER_SECRET = os.getenv('TWITTER_CONSUMER_SECRET', '')

NEOTTER_HOST_NAME = os.getenv('NEOTTER_HOST_NAME', 'localhost')
NEOTTER_PROTO = os.getenv('NEOTTER_PROTO', 'http')
NEOTTER_PORT = os.getenv('NEOTTER_SERVER_PORT', '')

if NEOTTER_PORT:
    NEOTTER_PORT = ':' + NEOTTER_PORT

twitter_api_host = 'https://api.twitter.com'
request_token_url = f'{twitter_api_host}/oauth/request_token'
authenticate_url = f'{twitter_api_host}/oauth/authenticate'
access_token_url = f'{twitter_api_host}/oauth/access_token'

oauth_callback = (f'{NEOTTER_PROTO}://'
                  f'{NEOTTER_HOST_NAME}{NEOTTER_PORT}/register')


def get_authenticate_endpoint():
    twitter = OAuth1Session(CONSUMER_KEY, CONSUMER_SECRET)

    response = twitter.post(
        request_token_url,
        params={'oauth_callback': oauth_callback}
    )

    request_token = dict(parse_qsl(response.content.decode("utf-8")))

    if 'oauth_token' not in request_token:
        logger.error('No oauth_token found. '
                     'Have you set TWITTER_CONSUMER_KEY/SECRET?')
        return None

    authenticate_endpoint = '%s?oauth_token=%s' \
        % (authenticate_url, request_token['oauth_token'])

    return authenticate_endpoint


def get_access_token(oauth_token: str, oauth_verifier: str):
    twitter = OAuth1Session(
        CONSUMER_KEY,
        CONSUMER_SECRET,
        oauth_token,
        oauth_verifier
    )

    response = twitter.post(
        access_token_url,
        params={'oauth_verifier': oauth_verifier}
    )

    access_token = dict(parse_qsl(response.content.decode("utf-8")))

    return access_token
