from typing import List, Dict
from logging import getLogger
from urllib.parse import quote

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
    message_list = map(
        lambda tw: Tweet.create(tw, neotter_user_id, contain_retweet=True).to_dict(),
        status_list_raw)
    user_list = map(
        lambda us: TwitterUser.create(us).to_dict(), map(
            lambda st: st.user, status_list_raw))
    status_list = []
    for mes, tweet_user in zip(message_list, user_list):
        mes.update(tweet_user)
        status_list.append(mes)
    return status_list


def get_status_list(user: NeotterUser, status_id_list_str: str) -> List[Dict]:
    status_id_list = _parse_parameter(status_id_list_str)
    if not status_id_list_str or not status_id_list:
        return ''
    api = _api_by_user(user)
    status_list_raw = api.GetStatuses(status_id_list)
    return _statuses_to_dict_list(status_list_raw, user.id)


def get_user_timeline(user: NeotterUser, twitter_user_id: str, count: int=50) -> List[Dict]:
    api = _api_by_user(user)
    user_timeline = api.GetUserTimeline(twitter_user_id, count=50)
    return _statuses_to_dict_list(user_timeline, user.id)


def get_search_result(user: NeotterUser, search_query: str) -> List[Dict]:
    query = {
        'term': search_query,
        'result_type': 'recent',
        'count': 50
    }
    api = _api_by_user(user)
    search_result = api.GetSearch(**query)
    return _statuses_to_dict_list(search_result, user.id)
