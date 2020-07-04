import json
import datetime
from urllib.parse import quote
from test_utils import db
from common import configs

DATETIME_FORMAT = configs.datetime_format


def _preprocess_message(message: dict):
    message['message'] = quote(message['message'])


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
    db.insert_from_dict('messages', messages)
    db.insert_from_dict('users', users)


def get_normal_tweets(data_id: str):
    with open(f'fixtures/normal_{data_id}_tweet.json') as f:
        db_tweet = json.load(f)
    return db_tweet


def get_db_data(delete: bool=False):
    messages = db.get_all_data('messages', 'message_id')
    users = db.get_all_data('users', 'user_id')
    if delete:
        db.delete_all_data('messages')
        db.delete_all_data('users')

    return messages, users


def tweets_to_model(tweets: list):
    return [Tweet(tweet) for tweet in tweets]


class User:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


class Tweet:
    def __init__(self, data: dict):
        for key, value in data.items():
            if key == 'user':
                value = User(**value)
            setattr(self, key, value)
