import collector.init_test

import unittest
import os
import copy
from common import configs
test_db_path = 'data/db.sqlite3'
configs.db_path = test_db_path

from twitter_client.collector import store_timeline
from lib import db_write
from test_utils import fixture


class TestCollector(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if os.path.exists(test_db_path):
            os.remove(test_db_path)
        db_write.migration()

        self.tweets_origin = fixture.get_normal_tweets('01')
        fixture.generate_normal_db('01')
        self.messages, self.users = fixture.get_db_data(delete=True)

    def setUp(self):
        self.tweets = copy.deepcopy(self.tweets_origin)

    def test_store_timeline(self):
        for neotter_user_id, tweet_dicts in self.tweets.items():
            tweets = fixture.tweets_to_model(tweet_dicts)
            store_timeline(tweets, neotter_user_id)
        messages, users = fixture.get_db_data()
        self.assertSequenceEqual(messages, self.messages)
        self.assertSequenceEqual(users, self.users)
