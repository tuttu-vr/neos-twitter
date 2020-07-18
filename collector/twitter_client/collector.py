import os
import urllib.parse
import sqlite3
import time
import datetime
import traceback
from logging import getLogger, DEBUG, StreamHandler

from dotenv import load_dotenv
import twitter as tw

from lib import db_write, db_read
from common.lib import crypt
from common.models import tweet, twitter_user

logger = getLogger(__name__)
logger.addHandler(StreamHandler())
logger.setLevel(DEBUG)

load_dotenv(verbose=True)

CONSUMER_KEY = os.getenv('TWITTER_CONSUMER_KEY', '')
CONSUMER_SECRET = os.getenv('TWITTER_CONSUMER_SECRET', '')

DATETIME_FORMAT = '%a %b %d %H:%M:%S %z %Y'


def get_twitter_api(access_token_key: str, access_token_secret: str):
    api = tw.Api(consumer_key=CONSUMER_KEY,
                 consumer_secret=CONSUMER_SECRET,
                 access_token_key=access_token_key,
                 access_token_secret=access_token_secret)
    return api


def get_search_result(api):
    query = {
        'q': '#NeosVR',
        'result_type': 'recent',
        'count': 10
    }
    query_raw = urllib.parse.urlencode(query)
    result = api.GetSearch(raw_query=query_raw)
    return result


NUM_TIMELINE_GET_COUNT = 100
TTL_HOUR_MESSAGES = 48
CRAWL_INTERVAL_SEC = 90


def get_user_timeline(user):
    logger.info('getting timeline for %s' % user['name'])

    access_key = crypt.decrypt(user['access_key'])
    access_secret = crypt.decrypt(user['access_secret'])

    try:
        api = get_twitter_api(access_key, access_secret)
        timeline = api.GetHomeTimeline(count=NUM_TIMELINE_GET_COUNT)
    except tw.TwitterError as e:
        logger.error(traceback.format_exc())
        time.sleep(1)
        return []
    else:
        logger.info('success getting timeline')
        return timeline


def store_timeline(timeline: list, user_id: str):
    logger.debug(f'Got {len(timeline)} tweets')
    user_list = tweet.extract_unique_users(timeline)
    tweet.add_all(timeline, user_id)
    twitter_user.add_all(user_list)


def main():
    while True:
        start_time = time.time()
        users = db_read.get_valid_neotter_users()
        for user in users:
            timeline = get_user_timeline(user)
            store_timeline(timeline, user['id'])
        db_write.delete_old_messages(hour_before=TTL_HOUR_MESSAGES)
        elapsed = time.time() - start_time
        if elapsed < CRAWL_INTERVAL_SEC:
            time.sleep(CRAWL_INTERVAL_SEC - elapsed)
        else:
            logger.warn('No interval because of many crawls.')


if __name__ == '__main__':
    main()
