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


def debug_timeline(timeline):
    logger.debug(timeline)
    for tweet in timeline:
        display = '%s | (%s) %s: %s' % (tweet.created_at, tweet.id, tweet.user.screen_name, tweet.text)
        logger.debug(display)


def tweet_to_dict(tweet, neotter_user_id):
    media = ''
    if tweet.media:
        media = ','.join(map(
            lambda m: m.media_url_https, filter(
                lambda m: m.type=='photo', tweet.media)))
    tweet_dic = {
        'message_id': '%s-%d' % (neotter_user_id, tweet.id),
        'message': tweet.text,
        'attachments': media,
        'user_id': tweet.user.id_str,
        'created_datetime': tweet.created_at,
        'client': 'twitter',
        'neotter_user_id': neotter_user_id
    }
    return tweet_dic


def escape_quote(text: str):
    return text.replace("'", "''")


def user_to_dict(user):
    return {
        'user_id': user.id_str,
        'name': f'{escape_quote(user.name)}@{user.screen_name}',
        'icon_url': user.profile_image_url_https,
        'client': 'twitter'
    }


def extract_timeline(timeline, neotter_user_id: str):
    tweet_list = []
    user_list = []
    for tweet in timeline:
        tweet_list.append(tweet_to_dict(tweet, neotter_user_id))
        user_list.append(user_to_dict(tweet.user))

    return tweet_list, user_list


def tweet_pipeline(tweet_list):
    rt_removed = list(filter(lambda tw: not tw['message'].startswith('RT '), tweet_list))
    for tw in rt_removed:
        tz_utc = datetime.timezone(datetime.timedelta(hours=0), 'UTC')
        tw['created_datetime'] = datetime.datetime.strptime(
            tw['created_datetime'], DATETIME_FORMAT).astimezone(tz_utc)
        tw['message'] = urllib.parse.quote(tw['message'])
    return rt_removed


def user_pipeline(user_list):
    user_set = {}
    for user in user_list:
        user_set[user['user_id']] = user
    return list(user_set.values())


NUM_TIMELINE_GET_COUNT = 100
TTL_HOUR_MESSAGES = 48


def get_user_timeline(user):
    logger.info('getting timeline for %s' % user['name'])

    access_key = crypt.decrypt(user['access_key'])
    access_secret = crypt.decrypt(user['access_secret'])

    api = get_twitter_api(access_key, access_secret)
    timeline = api.GetHomeTimeline(count=NUM_TIMELINE_GET_COUNT)
    logger.info('success getting timeline')
    return timeline


def store_timeline(timeline: list, user_id: str):
    logger.debug(f'Got {len(timeline)} tweets')
    tweet_list, user_list = extract_timeline(timeline, user_id)
    processed_tweet_list = tweet_pipeline(tweet_list)
    processed_user_list = user_pipeline(user_list)
    db_write.put_messages(processed_tweet_list)
    db_write.put_user(processed_user_list)


def main():
    while True:
        try:
            users = db_read.get_valid_neotter_users()
            for user in users:
                try:
                    timeline = get_user_timeline(user)
                except tw.TwitterError as e:
                    logger.error(traceback.format_exc())
                    time.sleep(1)
                store_timeline(timeline, user['id'])
            db_write.delete_old_messages(hour_before=TTL_HOUR_MESSAGES)
            time.sleep(90)
        except KeyboardInterrupt as e:
            logger.info('finish')
            break


if __name__ == '__main__':
    main()
