import traceback
from typing import List, Dict
from logging import getLogger
from urllib.parse import quote
from twitter import TwitterError

from common.models.neotter_user import NeotterUser
from common.models.tweet import Tweet
from common.models.twitter_user import TwitterUser
from common.lib import twitter
from lib.settings import TWEET_DELIMITER

from api.v2 import response

logger = getLogger(__name__)


def _parse_parameter(list_str: str) -> List[int]:
    try:
        return list(map(int, list_str.split(',')))
    except ValueError:
        raise ValueError(f'error: failed to parse request parameter')


def _api_by_user(user: NeotterUser):
    access_key, access_secret = user.get_auth_token()
    return twitter.get_twitter_api(access_key, access_secret)


def _statuses_to_dict_list(status_list_raw: list, neotter_user_id: str) -> List[Dict]:
    # need to be tested
    # neotter_user_id is not used
    status_list = []
    for status in status_list_raw:
        tweet = Tweet.create(status, neotter_user_id, contain_retweet=True)
        if not tweet:
            continue
        user = TwitterUser.create(status.user).to_dict()
        user.update(tweet.to_dict())
        status_list.append(user)
    return status_list


def get_status_list(user: NeotterUser, status_id_list_str: str) -> List[Dict]:
    status_id_list = _parse_parameter(status_id_list_str)
    if not status_id_list_str or not status_id_list:
        return ''
    api = _api_by_user(user)
    status_list_raw = api.GetStatuses(status_id_list)
    return _statuses_to_dict_list(status_list_raw, user.id)


def get_user_timeline(user: NeotterUser, twitter_user_id: str, count: int=50):
    api = _api_by_user(user)
    user_timeline = api.GetUserTimeline(twitter_user_id, count=50)
    if len(user_timeline) > 0:
        twitter_user_raw = user_timeline[0].user
        return twitter_user_raw, _statuses_to_dict_list(user_timeline, user.id)
    else:
        return None, None


def get_search_result(user: NeotterUser, search_query: str) -> List[Dict]:
    query = {
        'term': search_query,
        'result_type': 'recent',
        'count': 50
    }
    api = _api_by_user(user)
    search_result = api.GetSearch(**query)
    return _statuses_to_dict_list(search_result, user.id)


def post_message(user: NeotterUser, message: str, media_url_list: List[str]):
    api = _api_by_user(user)
    try:
        status = api.PostUpdate(message, media=media_url_list)
    except TwitterError:
        logger.error(traceback.format_exc())
        raise ValueError('Failed to post message to twitter')
    return status


def like_message(user: NeotterUser, message_id: str):
    api = _api_by_user(user)
    try:
        status = api.CreateFavorite(status_id=message_id)
    except TwitterError:
        logger.error(traceback.format_exc())
        raise ValueError(f'Failed to like message: id={message_id}')
    return status
