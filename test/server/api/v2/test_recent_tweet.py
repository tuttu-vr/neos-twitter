import server.init_test

import os
import json
import datetime
import unittest
from urllib.parse import unquote
from logging import getLogger

logger = getLogger(__name__)

from common import configs
from common.lib import db
test_db_path = 'data/db.sqlite3'
configs.db_path = test_db_path
DATETIME_FORMAT = configs.datetime_format

import app
from test_utils import fixture, parser, db as test_db


class TestRecentV2(unittest.TestCase):
    def setUp(self):
        if os.path.exists(test_db_path):
            os.remove(test_db_path)
        db.migration()
        fixture.generate_normal_db('01')
        self.db_data = fixture.get_db_data(delete=False, dict_row=True)
        self.tweets = fixture.get_normal_tweets('01')

    def test_auto_auth_limit_extention(self):
        count = 3
        offset = 0
        start_time = None
        expected_expiration = datetime.datetime.now() + datetime.timedelta(days=configs.auth_expiration_date)
        table_name = 'neotter_users'
        for user in self.db_data[table_name]:
            user_token = user['token']
            remote_addr = user['remote_addr']
            user_id = user['id']
            app._get_recent(count, offset, start_time, user_token, remote_addr, version='v2')
            data = test_db.get_single_data(table_name, {'id': user_id}, dict_row=True)
            got_expiration = datetime.datetime.strptime(data['expired'], DATETIME_FORMAT)
            self.assertLessEqual(abs(expected_expiration - got_expiration), datetime.timedelta(minutes=1))

    def test_get_recent(self):
        count = 3
        offset = 1
        start_time = '2020-07-03 15:01:00'
        table_name = 'neotter_users'
        results = {}
        expected = {
            '01': {
                'num_of_messages': 2,
                'messages': [
                    fixture.response_from_fixture(self.tweets['01'][2], version='v2'),
                    fixture.response_from_fixture(self.tweets['01'][3], version='v2')
                ]
            },
            '02': {
                'num_of_messages': 1,
                'messages': [
                    fixture.response_from_fixture(self.tweets['02'][1], version='v2')
                ]
            }
        }
        for user in self.db_data[table_name]:
            user_token = user['token']
            remote_addr = user['remote_addr']
            response = app._get_recent(count, offset, start_time, user_token, remote_addr, version='v2')
            parsed = parser.parse_response(response)
            results[user['id']] = parsed
            expected_data = expected[user['id']]
            for key, value in expected_data.items():
                self.assertEqual(parsed[key], value)
        print(json.dumps(results, ensure_ascii=False, indent=4))
