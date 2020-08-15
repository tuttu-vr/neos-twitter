from logging import getLogger
import traceback
from sqlalchemy import and_, desc
from sqlalchemy.exc import OperationalError, InternalError
from twitter import Status

from common.models.tweet import Tweet
from common.models.twitter_user import TwitterUser
from common.lib import db

logger = getLogger(__name__)


def _merge_result(messages: list):
    result = []
    for tw, user in messages:
        message = tw.to_dict()
        message.update(user.to_dict())
        result.append(message)
    return result


def get_recent_messages(
        count: int, offset: int, start_time: str, user_id: str):
    logger.info('getting messages')
    session = db.get_session()
    try:
        messages = session.query(Tweet, TwitterUser) \
            .join(TwitterUser, and_(
                Tweet.user_id == TwitterUser.user_id,
                Tweet.client == TwitterUser.client)) \
            .filter(
                Tweet.neotter_user_id == user_id,
                Tweet.created_datetime >= start_time) \
            .order_by(Tweet.created_datetime) \
            .limit(count).offset(offset)
    except (OperationalError, InternalError):
        logger.error(traceback.format_exc())
    finally:
        session.close()
    return _merge_result(messages)


def get_timeline_messages(user_id: str, from_id: str = 0, count: int = 10):
    session = db.get_session()
    try:
        messages = session.query(Tweet, TwitterUser) \
            .join(TwitterUser, and_(
                Tweet.user_id == TwitterUser.user_id,
                Tweet.client == TwitterUser.client))
        if from_id:
            from_id_db = f'{user_id}-{from_id}'
            messages = messages.filter(
                Tweet.neotter_user_id == user_id,
                Tweet.message_id > from_id_db) \
                .order_by(Tweet.created_datetime).limit(count).all()
        else:
            messages = reversed(
                messages.filter(Tweet.neotter_user_id == user_id)
                .order_by(desc(Tweet.created_datetime)).limit(count).all())
    except (OperationalError, InternalError):
        logger.error(traceback.format_exc())
    finally:
        session.close()
    return _merge_result(messages)


def extract_tweet_and_user(
        status: Status, neotter_user_id: str,
        extract_retweet: bool = True) -> (Tweet, TwitterUser):
    if extract_retweet and status.retweeted_status:
        logger.debug(status.retweeted_status)
        status = status.retweeted_status
    tweet = Tweet.create(status, neotter_user_id)
    if not tweet:
        return None, None
    user = TwitterUser.create(status.user)
    return tweet, user
