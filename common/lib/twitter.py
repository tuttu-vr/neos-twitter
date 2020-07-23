import os
import twitter as tw

CONSUMER_KEY = os.getenv('TWITTER_CONSUMER_KEY', '')
CONSUMER_SECRET = os.getenv('TWITTER_CONSUMER_SECRET', '')


def get_twitter_api(access_token_key: str, access_token_secret: str):
    api = tw.Api(consumer_key=CONSUMER_KEY,
                 consumer_secret=CONSUMER_SECRET,
                 access_token_key=access_token_key,
                 access_token_secret=access_token_secret)
    return api
