import os
import urllib.parse
import sqlite3
import time
import datetime
import traceback
from logging import getLogger, DEBUG, StreamHandler

from dotenv import load_dotenv
import twitter as tw

from common.lib import crypt, twitter
from common.models import tweet, twitter_user, neotter_user

logger = getLogger(__name__)
logger.addHandler(StreamHandler())
logger.setLevel(DEBUG)

load_dotenv(verbose=True)

DATETIME_FORMAT = '%a %b %d %H:%M:%S %z %Y'


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
        api = twitter.get_twitter_api(access_key, access_secret)
        timeline = api.GetHomeTimeline(count=NUM_TIMELINE_GET_COUNT)
    except tw.TwitterError:
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


def delete_expired():
    tweet.delete_old_tweets(hour_before=TTL_HOUR_MESSAGES)
    neotter_user.delete_expired_users()


def get_neotter_users():
    return neotter_user.get_valid_users()


def main():
    while True:
        start_time = time.time()
        for user in get_neotter_users():
            timeline = get_user_timeline(user)
            store_timeline(timeline, user['id'])
        delete_expired()
        elapsed = time.time() - start_time
        logger.info(f'Elapsed time to crawl: {elapsed}s')
        if elapsed < CRAWL_INTERVAL_SEC:
            time.sleep(CRAWL_INTERVAL_SEC - elapsed)
        else:
            logger.warn('No interval because of many crawls.')


if __name__ == '__main__':
    main()
