import json
import datetime
from urllib.parse import quote
from test_utils import db
from common import configs

DATETIME_FORMAT = configs.datetime_format


def _preprocess_message(message: dict):
    message['message'] = quote(message['message'])
    if type(message['created_datetime']) == int:
        message['created_datetime'] = _generate_relative_date(message['created_datetime'])


def _generate_relative_date(day: int):
    return (datetime.datetime.now() + datetime.timedelta(days=day)).strftime(DATETIME_FORMAT)


def _preprocess_neotter_user(user: dict):
    if type(user['expired']) == int:
        user['expired'] = _generate_relative_date(user['expired'])
    if type(user['last_login']) == int:
        user['last_login'] = _generate_relative_date(user['last_login'])


def _preprocess(data_list: list, process_func=None):
    results = []
    for data in data_list:
        if not data['insert']:
            continue
        if process_func:
            process_func(data)
        del data['insert']
        results.append(data)
    return results


def generate_normal_db(data_id: str):
    with open(f'fixtures/normal_{data_id}_db.json') as f:
        db_json = json.load(f)

    messages = _preprocess(db_json['messages'], _preprocess_message)
    users = _preprocess(db_json['users'])
    neotter_users = _preprocess(db_json['neotter_users'], _preprocess_neotter_user)
    db.insert_from_dict('messages', messages)
    db.insert_from_dict('users', users)
    db.insert_from_dict('neotter_users', neotter_users)


def get_normal_tweets(data_id: str):
    with open(f'fixtures/normal_{data_id}_tweet.json') as f:
        db_tweet = json.load(f)
    return db_tweet


def response_from_fixture(tweet: dict, version: str='v1'):
    process = {
        'v1': _response_from_fixture_v1,
        'v2': _response_from_fixture_v2
    }
    return process[version](tweet)


def _response_from_fixture_v1(tweet: dict):
    datetime_format = '%a %b %d %H:%M:%S %z %Y'
    return {
        'created_at': datetime.datetime.strptime(tweet['created_at'], datetime_format)
            .strftime(DATETIME_FORMAT),
        'user.name': '%s@%s' % (tweet['user']['name'], tweet['user']['screen_name']),
        'user.profile_image_url_https': tweet['user']['profile_image_url_https'],
        'media': tweet['media'],
        'text': tweet['text']
    }


def _response_from_fixture_v2(tweet: dict):
    datetime_format = '%a %b %d %H:%M:%S %z %Y'
    return {
        'id': tweet['id'],
        'created_at': datetime.datetime.strptime(tweet['created_at'], datetime_format)
            .strftime(DATETIME_FORMAT),
        'user.name': '%s@%s' % (tweet['user']['name'], tweet['user']['screen_name']),
        'user.profile_image_url_https': tweet['user']['profile_image_url_https'],
        'media': tweet['media'],
        'text': tweet['text'],
        'favorite_count': tweet['favorite_count'],
        'retweet_count': tweet['retweet_count'],
        'favorited': str(tweet['favorited']),
        'retweeted': str(tweet['retweeted'])
    }


def get_db_data(delete: bool=False, dict_row: bool=False):
    db_list = {
        'messages': 'message_id',
        'users': 'user_id',
        'neotter_users': 'id'
    }
    result = {}
    for table_name, sort_key in db_list.items():
        result[table_name] = db.get_all_data(table_name, sort_key, dict_row)
        if delete:
            db.delete_all_data(table_name)
    return result


def tweets_to_model(tweets: list):
    return [TestStatus(tweet) for tweet in tweets]


class TestUser:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


class TestStatus:
    def __init__(self, data: dict):
        for key, value in data.items():
            if key == 'user':
                value = TestUser(**value)
            setattr(self, key, value)
