from typing import List, Dict
import datetime
import traceback
from urllib.parse import quote
from logging import getLogger

from lib import twitter
from lib.settings import TWEET_DELIMITER, DATETIME_FORMAT
from lib.model_utils import messages as mes_lib
from common.models.neotter_user import NeotterUser
from common.models.twitter_user import TwitterUser

logger = getLogger(__name__)

DELIMITER = TWEET_DELIMITER

TIMEZONE_LOCAL = datetime.timezone(datetime.timedelta(hours=+9), 'JST')
TIMEZONE_UTC = datetime.timezone(datetime.timedelta(hours=+0), 'UTC')

TWEET_URL_TEMPLATE = 'https://twitter.com/%s/status/%s'


def _process_message(mes: dict, blacklist: List[str]=[]) -> str:
    utc_time = datetime.datetime.strptime(mes['created_datetime'], DATETIME_FORMAT).replace(tzinfo=TIMEZONE_UTC)
    local_time_str = utc_time.astimezone(TIMEZONE_LOCAL).strftime(DATETIME_FORMAT)
    try:
        screen_name = mes['name'].split('@')[-1]
        tweet_id = mes['message_id'].split('-')[1]
        processed = {
            'id'            : tweet_id, # TODO keep original id on DB
            'created_at'    : quote(local_time_str),
            'name'          : quote(mes['name']),
            'user_id'       : mes['user_id'],
            'icon_url'      : quote(mes['icon_url']),
            'tweet_url'     : quote(TWEET_URL_TEMPLATE % (screen_name, tweet_id)),
            'attachments'   : (quote(mes['attachments']) if mes['attachments'] else ''),
            'message'       : mes['message'],
            'favorite_count': str(mes['favorite_count']),
            'retweet_count' : str(mes['retweet_count']),
            'favorited'     : str(mes['favorited']),
            'retweeted'     : str(mes['retweeted'])
        }
        for key in blacklist:
            del processed[key]
        result = ';'.join([f'{key}={value}' for key, value in processed.items()])
        return result
    except TypeError:
        logger.error(traceback.format_exc())
        for key in mes.keys():
            logger.error('%s=%s' % (key, str(mes[key])))
        return None


def _process_messages(messages: List[dict]) -> List[str]:
    text_list = list(filter(lambda x: x, [_process_message(mes) for mes in messages]))
    return text_list


def _process_profile(twitter_user_raw: dict):
    parameters = {
        'id_str': 'user_id',
        'name': 'user_name',
        'screen_name': 'screen_name',
        'profile_banner_url': 'profile_banner',
        'profile_image_url_https': 'profile_image',
        'description': 'description'
    }
    user_dict = twitter_user_raw.AsDict()
    if 'profile_banner_url' not in user_dict:
        user_dict['profile_banner_url'] = 'https://placehold.jp/1500x500.png'
    result = ';'.join([
        f'{neotter_key}={quote(user_dict[key])}' for key, neotter_key in parameters.items()
    ])
    return result


def _join_to_str(status_list: List[Dict]) -> str:
    return DELIMITER.join(_process_messages(status_list))


def get_recent_response(messages: List[Dict], start_time: str) -> str:
    text_list = _process_messages(messages)
    text_list_str = DELIMITER.join(text_list)
    return f'{start_time}|{len(text_list)}|{text_list_str}'


def get_home_timeline(user: NeotterUser, from_id: str=0, count: int=10) -> str:
    timeline = mes_lib.get_timeline_messages(user.id, from_id, count)
    return _join_to_str(timeline)


def get_status_list(status_id_list_str: str, user: NeotterUser) -> str:
    status_list = twitter.get_status_list(user, status_id_list_str)
    return _join_to_str(status_list)


def get_user_timeline(user: NeotterUser, twitter_user_id: str) -> str:
    twitter_user_raw, user_timeline = twitter.get_user_timeline(user, twitter_user_id)
    if twitter_user_raw is None:
        logger.info('No user found by: %s %s' % (twitter_user_id, user.name))
        return 'No User Found'
    return f'{_process_profile(twitter_user_raw)}|{_join_to_str(user_timeline)}'


def get_search_result(user: NeotterUser, query: str) -> str:
    """
    query must be decoded
    """
    logger.info('Search query: %s by %s' % (query, user.name))
    search_result = twitter.get_search_result(user, query)
    return _join_to_str(search_result)


MESSAGE_ERROR_POST = 'Something went wrong. Please check your twitter status.'


def create_message(user: NeotterUser, message: str, media_list: List[str]):
    # TODO validate url
    status = twitter.post_message(user, message, media_list)
    if status: # TODO check status
        return _process_message(status)
    else:
        raise ValueError(MESSAGE_ERROR_POST)


def create_like(user: NeotterUser, message_id: str):
    status = twitter.like_message(user, message_id)
    if status:
        return _process_message(status)
    else:
        raise ValueError(MESSAGE_ERROR_POST)


def create_retweet(user: NeotterUser, message_id: str):
    status = twitter.retweet_message(user, message_id)
    if status:
        return _process_message(status)
    else:
        raise ValueError(MESSAGE_ERROR_POST)
