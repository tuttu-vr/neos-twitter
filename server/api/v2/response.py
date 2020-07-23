from typing import List, Dict
import datetime
import traceback
from urllib.parse import quote
from logging import getLogger

from lib import twitter
from lib.settings import TWEET_DELIMITER, DATETIME_FORMAT
from common.models.neotter_user import NeotterUser
from common.models.twitter_user import TwitterUser

logger = getLogger(__name__)

DELIMITER = TWEET_DELIMITER

TIMEZONE_LOCAL = datetime.timezone(datetime.timedelta(hours=+9), 'JST')
TIMEZONE_UTC = datetime.timezone(datetime.timedelta(hours=+0), 'UTC')


def _process_messages(messages: List[Dict]) -> List[str]:
    def process_message(mes):
        utc_time = datetime.datetime.strptime(mes['created_datetime'], DATETIME_FORMAT).replace(tzinfo=TIMEZONE_UTC)
        local_time_str = utc_time.astimezone(TIMEZONE_LOCAL).strftime(DATETIME_FORMAT)
        try:
            return ';'.join([
                'id=' + mes['message_id'].split('-')[1], # TODO keep original id on DB
                'created_at=' + quote(local_time_str),
                'name=' + quote(mes['name']),
                'icon_url=' + quote(mes['icon_url']),
                'attachments=' + (quote(mes['attachments']) if mes['attachments'] else ''),
                'message=' + mes['message'],
                'favorite_count=%d' % mes['favorite_count'],
                'retweet_count=%d' % mes['retweet_count'],
                'favorited=' + str(mes['favorited']),
                'retweeted=' + str(mes['retweeted'])
            ])
        except TypeError:
            logger.error(traceback.format_exc())
            for key in mes.keys():
                logger.error('%s=%s' % (key, str(mes[key])))
            return None
    text_list = list(filter(lambda x: x, [process_message(mes) for mes in messages]))
    return text_list


def _join_to_str(status_list: List[Dict]) -> str:
    return DELIMITER.join(_process_messages(status_list))


def get_recent_response(messages: List[Dict], start_time: str) -> str:
    text_list = _process_messages(messages)
    text_list_str = DELIMITER.join(messages)
    return f'{start_time}|{len(text_list)}|{text_list_str}'


def get_status_list(status_id_list_str: str, user: NeotterUser) -> str:
    status_list = twitter.get_status_list(user, status_id_list_str)
    return _join_to_str(status_list)


def get_user_timeline(user: NeotterUser, twitter_user_id: str) -> str:
    user_timeline = twitter.get_user_timeline(user, twitter_user_id)
    return _join_to_str(user_timeline)


def get_search_result(user: NeotterUser, query: str) -> str:
    """
    query must be decoded
    """
    search_result = twitter.get_search_result(user, query)
    return _join_to_str(search_result)