import json
import requests
import argparse
import time
from logging import getLogger, DEBUG, StreamHandler

from test_utils import parser

DELIMITER = '$'
logger = getLogger(__name__)
logger.setLevel(DEBUG)
logger.addHandler(StreamHandler())
endpoint = 'http://localhost:8080/api/v2/'


def load_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('key')
    return parser.parse_args()


def dump_request(api_name: str, query: dict):
    res = requests.get(endpoint + api_name, query)
    logger.info(api_name)
    logger.info(res.text)
    for message_str in res.text.split(DELIMITER):
        message = parser.parse_message(message_str)
        logger.info(json.dumps(message, indent=4, ensure_ascii=False))


def test_get_status_list(key: str, id_list: list=['1286075295468892160', '1286202545065431042']):
    status_id_list = ','.join(id_list)
    query = {
        'key': key,
        'status_ids': status_id_list
    }
    dump_request('status-list', query)


def test_get_user_timeline(key: str, user_id: str='1213118571045240835'):
    query = {
        'key': key,
        'user_id': user_id
    }
    dump_request('user-timeline', query)


def test_get_search_result(key: str, query: str='#NeosVR'):
    query = {
        'key': key,
        'query': query
    }
    dump_request('search-result', query)


if __name__ == '__main__':
    args = load_args()
    test_get_status_list(args.key)
    time.sleep(0.5)
    test_get_user_timeline(args.key)
    time.sleep(0.5)
    test_get_search_result(args.key)
