import collector.init_test

import unittest
import os
import copy
from common import configs
from common.lib import db
test_db_path = 'data/db.sqlite3'
configs.db_path = test_db_path

from twitter_client.collector import store_timeline, delete_expired, get_neotter_users
from test_utils import fixture


class TestCollector(unittest.TestCase):
    def setUp(self):
        if os.path.exists(test_db_path):
            os.remove(test_db_path)
        db.migration()

    def test_store_timeline(self):
        tweets = fixture.get_normal_tweets('01')
        fixture.generate_normal_db('01')
        db_data = fixture.get_db_data(delete=True)
        messages = db_data['messages']
        users = db_data['users']

        for neotter_user_id, tweet_dicts in tweets.items():
            tweets = fixture.tweets_to_model(tweet_dicts)
            store_timeline(tweets, neotter_user_id)
        db_data = fixture.get_db_data()
        self.assertSequenceEqual(db_data['messages'], messages)
        self.assertSequenceEqual(db_data['users'], users)

    def test_delete_expired(self):
        fixture.generate_normal_db('expired')
        db_data = fixture.get_db_data()

        delete_expired()
        test_data = fixture.get_db_data()
        expected_messages = [db_data['messages'][1]]
        self.assertSequenceEqual(test_data['messages'], expected_messages)

        expected_users = [db_data['neotter_users'][0]]
        self.assertSequenceEqual(test_data['neotter_users'], expected_users)

    def test_get_valid_users(self):
        fixture.generate_normal_db('expired')
        db_data = fixture.get_db_data(dict_row=True)

        expected_users = [db_data['neotter_users'][0]]
        neotter_users = get_neotter_users()
        self.assertEqual(len(expected_users), len(neotter_users))
        for expected, got in zip(expected_users, neotter_users):
            self.assertSequenceEqual(sorted(expected.keys()), sorted(got.keys()))
            for key in got.keys():
                self.assertEqual(expected[key], got[key])
