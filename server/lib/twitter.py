import traceback
from typing import List, Dict
from logging import getLogger
from twitter import TwitterError, Status

from common.models.neotter_user import NeotterUser
from common.lib import twitter
from lib.model_utils.messages import extract_tweet_and_user

logger = getLogger(__name__)


def _parse_parameter(list_str: str) -> List[int]:
    try:
        return list(map(int, list_str.split(',')))
    except ValueError:
        raise ValueError('error: failed to parse request parameter')


def _api_by_user(user: NeotterUser):
    access_key, access_secret = user.get_auth_token()
    return twitter.get_twitter_api(access_key, access_secret)


def _merge_status_and_user(status: Status, neotter_user_id: str) -> dict:
    tweet, user = extract_tweet_and_user(status, neotter_user_id)
    response = user.to_dict()
    response.update(tweet.to_dict())
    return response


def _statuses_to_dict_list(
        status_list_raw: list, neotter_user_id: str,
        distinct: bool = False) -> List[Dict]:
    # need to be tested
    # neotter_user_id is not used
    uniques = set()
    status_list = []
    for status in status_list_raw:
        merged = _merge_status_and_user(status, neotter_user_id)
        if distinct and merged['message_id'] in uniques:
            continue
        status_list.append(merged)
        uniques.add(merged['message_id'])
    return status_list


def get_status_list(user: NeotterUser, status_id_list_str: str) -> List[Dict]:
    status_id_list = _parse_parameter(status_id_list_str)
    if not status_id_list_str or not status_id_list:
        return ''
    api = _api_by_user(user)
    status_list_raw = api.GetStatuses(status_id_list)
    return _statuses_to_dict_list(status_list_raw, user.id)


def update_statuses(api, status_list: list) -> Status:
    status_list_ids = list(map(lambda tw: tw.id_str, status_list))
    status_list_updated = api.GetStatuses(status_list_ids)
    return status_list_updated


def get_user_timeline(
        user: NeotterUser, twitter_user_id: str, count: int = 50):
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
    search_result = update_statuses(api, api.GetSearch(**query))
    return _statuses_to_dict_list(search_result, user.id, distinct=True)


def post_message(user: NeotterUser, message: str, media_url_list: List[str]):
    api = _api_by_user(user)
    try:
        media_id_list = [api.UploadMediaSimple(url) for url in media_url_list]
        status = api.PostUpdate(message, media=media_id_list)
        if status.full_text is None:
            status.full_text = status.text
        tweet = _merge_status_and_user(status, user.id)
    except TwitterError:
        logger.error(traceback.format_exc())
        raise ValueError('Failed to post message to twitter')
    return tweet


def like_message(user: NeotterUser, message_id: str):
    api = _api_by_user(user)
    try:
        status = api.CreateFavorite(status_id=message_id)
        if status.full_text is None:
            status.full_text = status.text
        tweet = _merge_status_and_user(status, user.id)
    except TwitterError:
        logger.error(traceback.format_exc())
        raise ValueError(f'Failed to like message: id={message_id}')
    return tweet


def retweet_message(user: NeotterUser, message_id: str):
    api = _api_by_user(user)
    try:
        status = api.PostRetweet(message_id)
        if status.full_text is None:
            status.full_text = status.text
        tweet = _merge_status_and_user(status, user.id)
    except TwitterError:
        logger.error(traceback.format_exc())
        raise ValueError(f'Failed to retweet message: id={message_id}')
    return tweet
