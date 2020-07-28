import server.init_test

import os
import json
import datetime
import unittest
from urllib.parse import unquote
from logging import getLogger

logger = getLogger(__name__)

from lib.settings import TWEET_DELIMITER
from common import configs
from common.lib import db
from common.models import neotter_user
test_db_path = 'data/db.sqlite3'
configs.db_path = test_db_path
DATETIME_FORMAT = configs.datetime_format

import app
from test_utils import fixture, parser, db as test_db

TIMEZONE_UTC = configs.TIMEZONE_UTC
TIMEZONE_LOCAL = configs.TIMEZONE_LOCAL


class TestHomeTimeline(unittest.TestCase):
    def setUp(self):
        if os.path.exists(test_db_path):
            os.remove(test_db_path)
        db.migration()
        fixture.generate_normal_db('01')
        self.db_data = fixture.get_db_data(delete=False, dict_row=True)
        self.tweets = fixture.get_normal_tweets('01')

    def test_auto_auth_limit_extention(self):
        count = 3
        from_id = 0
        expected_expiration = datetime.datetime.now(tz=TIMEZONE_UTC) + datetime.timedelta(days=configs.auth_expiration_date)
        table_name = 'neotter_users'
        for user in self.db_data[table_name]:
            user_token = user['token']
            user_id = user['id']
            n_user = neotter_user.get_by_token(user_token)
            app._get_home_timeline(n_user, from_id, count)
            data = test_db.get_single_data(table_name, {'id': user_id}, dict_row=True)
            got_expiration = datetime.datetime.strptime(data['expired'], DATETIME_FORMAT) \
                .replace(tzinfo=TIMEZONE_UTC)
            self.assertLessEqual(abs(expected_expiration - got_expiration), datetime.timedelta(minutes=1))

    def _test_home_timeline(self, params: dict, expected: dict):
        count = params['count']
        from_id = params['from_id']
        table_name = 'neotter_users'
        results = {}
        for user in self.db_data[table_name]:
            user_token = user['token']
            n_user = neotter_user.get_by_token(user_token)
            response = app._get_home_timeline(n_user, from_id, count)

            parsed = []
            for message_str in response.split(TWEET_DELIMITER):
                message = parser.parse_message(message_str)
                parsed.append(message)
            # TODO
            results[user['id']] = parsed
            expected_data = expected[user['id']]
            self.assertEqual(parsed, expected_data)
        print(json.dumps(results, ensure_ascii=False, indent=4))

    def test_home_timeline(self):
        params_1 = {
            'count': 2,
            'from_id': 1002
        }
        expected_1 = {
            '01': [
                fixture.response_from_fixture(self.tweets['01'][2], version='v2'),
                fixture.response_from_fixture(self.tweets['01'][3], version='v2')
            ],
            '02': [
                fixture.response_from_fixture(self.tweets['02'][1], version='v2')
            ]
        }
        self._test_home_timeline(params_1, expected_1)

        params_2 = {
            'count': 2,
            'from_id': 0
        }
        expected_2 = {
            '01': [
                fixture.response_from_fixture(self.tweets['01'][2], version='v2'),
                fixture.response_from_fixture(self.tweets['01'][3], version='v2')
            ],
            '02': [
                fixture.response_from_fixture(self.tweets['02'][0], version='v2'),
                fixture.response_from_fixture(self.tweets['02'][1], version='v2'),
            ]
        }
        self._test_home_timeline(params_2, expected_2)
