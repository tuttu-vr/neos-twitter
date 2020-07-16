import collector.init_test

import unittest
import os
import copy
from common import configs
from common.lib import db
test_db_path = 'data/db.sqlite3'
configs.db_path = test_db_path

from twitter_client.collector import store_timeline
from test_utils import fixture


class TestCollector(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if os.path.exists(test_db_path):
            os.remove(test_db_path)
        db.migration()

        self.tweets_origin = fixture.get_normal_tweets('01')
        fixture.generate_normal_db('01')
        db_data = fixture.get_db_data(delete=True)
        self.messages = db_data['messages']
        self.users = db_data['users']

    def setUp(self):
        self.tweets = copy.deepcopy(self.tweets_origin)

    def test_store_timeline(self):
        for neotter_user_id, tweet_dicts in self.tweets.items():
            tweets = fixture.tweets_to_model(tweet_dicts)
            store_timeline(tweets, neotter_user_id)
        db_data = fixture.get_db_data()
        self.assertSequenceEqual(db_data['messages'], self.messages)
        self.assertSequenceEqual(db_data['users'], self.users)
