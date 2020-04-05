import os
import urllib.parse
import sqlite3
import time
import datetime
from logging import getLogger, DEBUG, StreamHandler

from dotenv import load_dotenv
import twitter as tw

import lib.db_write as db

logger = getLogger(__name__)
logger.addHandler(StreamHandler())
logger.setLevel(DEBUG)

load_dotenv(verbose=True)

CONSUMER_KEY = os.getenv('TWITTER_CONSUMER_KEY', '')
CONSUMER_SECRET = os.getenv('TWITTER_CONSUMER_SECRET', '')
ACCESS_TOKEN = os.getenv('TWITTER_ACCESS_TOKEN', '')
ACCESS_SECRET = os.getenv('TWITTER_ACCESS_SECRET', '')

DATETIME_FORMAT = '%a %b %d %H:%M:%S %z %Y'


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


def tweet_to_dict(tweet):
    media = ''
    if tweet.media:
        media = ','.join(map(
            lambda m: m.media_url_https, filter(
                lambda m: m.type=='photo', tweet.media)))
    tweet_dic = {
        'message_id': tweet.id,
        'message': tweet.text,
        'attachments': media,
        'user_id': tweet.user.id_str,
        'created_datetime': tweet.created_at,
        'client': 'twitter'
    }
    return tweet_dic


def user_to_dict(user):
    return {
        'user_id': user.id_str,
        'name': f'{user.name}@{user.screen_name}',
        'icon_url': user.profile_image_url_https,
        'client': 'twitter'
    }


def extract_timeline(timeline):
    tweet_list = []
    user_list = []
    for tweet in timeline:
        tweet_list.append(tweet_to_dict(tweet))
        user_list.append(user_to_dict(tweet.user))

    return tweet_list, user_list


def tweet_pipeline(tweet_list):
    rt_removed = list(filter(lambda tw: not tw['message'].startswith('RT '), tweet_list))
    for tw in rt_removed:
        tw['created_datetime'] = datetime.datetime.strptime(tw['created_datetime'], DATETIME_FORMAT)
    return rt_removed


def user_pipeline(user_list):
    user_set = {}
    for user in user_list:
        user_set[user['user_id']] = user
    return list(user_set.values())


def store_timeline(timeline):
    logger.debug(f'Got {len(timeline)} tweets')
    tweet_list, user_list = extract_timeline(timeline)
    processed_tweet_list = tweet_pipeline(tweet_list)
    processed_user_list = user_pipeline(user_list)
    db.put_messages(processed_tweet_list)
    db.put_user(processed_user_list)


NUM_TIMELINE_GET_COUNT = 50
TTL_HOUR_MESSAGES = 48

def main():
    api = get_twitter_api()
    while True:
        try:
            logger.info('getting timeline')
            timeline = api.GetHomeTimeline(count=NUM_TIMELINE_GET_COUNT)
            logger.info('success getting timeline')
            store_timeline(timeline)
            db.delete_old_messages(hour_before=TTL_HOUR_MESSAGES)
            time.sleep(90)
        except KeyboardInterrupt as e:
            logger.info('finish')
            break
        except tw.TwitterError as e:
            logger.error(e)
            time.sleep(10 * 60)


if __name__ == '__main__':
    main()
