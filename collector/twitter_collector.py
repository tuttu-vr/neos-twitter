import os
import urllib.parse
import sqlite3
import time

from logging import getLogger, DEBUG, StreamHandler

from dotenv import load_dotenv
import twitter as tw

import db_write as db

logger = getLogger(__name__)
logger.addHandler(StreamHandler())
logger.setLevel(DEBUG)

load_dotenv(verbose=True)

CONSUMER_KEY = os.getenv('TWITTER_CONSUMER_KEY', '')
CONSUMER_SECRET = os.getenv('TWITTER_CONSUMER_SECRET', '')
ACCESS_TOKEN = os.getenv('TWITTER_ACCESS_TOKEN', '')
ACCESS_SECRET = os.getenv('TWITTER_ACCESS_SECRET', '')


def get_twitter_api():
    api = tw.Api(consumer_key=CONSUMER_KEY,
                 consumer_secret=CONSUMER_SECRET,
                 access_token_key=ACCESS_TOKEN,
                 access_token_secret=ACCESS_SECRET)
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


def debug_timeline(timeline):
    logger.debug(timeline)
    for tweet in timeline:
        display = '%s | (%s) %s: %s' % (tweet.created_at, tweet.id, tweet.user.screen_name, tweet.text)
        logger.debug(display)


def timeline_to_dict_iter(timeline):
    return map(lambda t: {
        'message_id': t.id,
        'message': t.text,
        'name': t.user.screen_name,
        'created_datetime': t.created_at
    }, timeline)


def pipeline(timeline_iter):
    rt_removed = filter(lambda tw: not tw['message'].startswith('RT '), timeline_iter)
    line_formatted = map(lambda tw: tw['message'] = tw['message'].replace('\n', ' '), rt_removed)
    return line_formatted


def store_timeline(timeline):
    timeline_iter = timeline_to_dict_iter(timeline)
    timeline_iter = pipeline(timeline_iter)
    db.put_messages(list(timeline_iter))


NUM_TIMELINE_GET_COUNT = 50

def main():
    api = get_twitter_api()
    while True:
        try:
            logger.info('getting timeline')
            timeline = api.GetHomeTimeline(count=NUM_TIMELINE_GET_COUNT)
            logger.info('success getting timeline')
            store_timeline(timeline)
            time.sleep(60)
        except KeyboardInterrupt as e:
            logger.info('finish')
            break


if __name__ == '__main__':
    db.migration()
    main()
