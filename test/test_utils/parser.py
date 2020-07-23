import datetime
from urllib.parse import unquote

from lib.settings import TWEET_DELIMITER
from common import configs

DATETIME_FORMAT = configs.datetime_format

TIMEZONE_JST = datetime.timezone(datetime.timedelta(hours=+9), 'JST')
TIMEZONE_UTC = datetime.timezone(datetime.timedelta(hours=+0), 'UTC')


def parse_message(mes: str) -> dict:
    message_data = {key: value for key, value in map(lambda m: tuple(m.split('=')), mes.split(';'))}
    message = {
        'id': int(message_data['id']),
        'created_at': datetime.datetime.strptime(unquote(message_data['created_at']), DATETIME_FORMAT)
            .replace(tzinfo=TIMEZONE_JST).astimezone(TIMEZONE_UTC).strftime(DATETIME_FORMAT),
        'user.name': unquote(message_data['name']),
        'user.id': message_data['user_id'],
        'user.profile_image_url_https': unquote(message_data['icon_url']),
        'media': list(map(unquote, message_data['attachments'].split(','))),
        'text': unquote(message_data['message']),
        'favorite_count': int(message_data['favorite_count']),
        'retweet_count': int(message_data['retweet_count']),
        'favorited': message_data['favorited'],
        'retweeted': message_data['retweeted']
    }
    if message_data['attachments'] == '':
        message['media'] = []
    return message


def parse_response(response: str):
    data = response.split('|')
    message_list = data[2].split(TWEET_DELIMITER)
    messages = []
    parsed = {
        'datetime': datetime.datetime.strptime(data[0], DATETIME_FORMAT)
            .replace(tzinfo=TIMEZONE_JST).astimezone(TIMEZONE_UTC).strftime(DATETIME_FORMAT),
        'num_of_messages': int(data[1]),
        'messages': messages
    }
    for mes in message_list:
        message = parse_message(mes)
        parsed['messages'].append(message)
    return parsed
