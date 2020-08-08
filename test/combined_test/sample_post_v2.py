import json
from urllib.parse import unquote
import requests
import argparse
import time
from logging import getLogger, DEBUG, StreamHandler

logger = getLogger(__name__)
logger.setLevel(DEBUG)
logger.addHandler(StreamHandler())
endpoint = 'http://localhost:8080/api/v2/'


def post_tweet(key: str, message: str, media: list=[]):
    params = {
        'message': message,
        'key': key,
        'media': ','.join(media)
    }
    response = requests.post(endpoint + 'message', params)
    logger.info(response.text)


def like_tweet(key: str, message_id: str):
    params = {
        'message_id': message_id,
        'key': key
    }
    response = requests.post(endpoint + 'like', params)
    logger.info(response.text)


def load_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('key')
    return parser.parse_args()


if __name__ == '__main__':
    args = load_args()
    post_tweet(args.key, '画像テスト2', [
        'https://placehold.jp/150x150.png',
        'http://placehold.jp/24/cc9999/993333/150x100.png'
    ])
    # like_tweet(args.key, 'xxxxxx')
