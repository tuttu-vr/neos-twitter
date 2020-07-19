from logging import getLogger
import traceback
from sqlalchemy import and_
from sqlalchemy.exc import OperationalError, InternalError

from common.models.tweet import Tweet
from common.models.twitter_user import TwitterUser
from common.lib import db

logger = getLogger(__name__)


def get_recent_messages(count: int, offset: int, start_time: str, user_id: str):
    logger.info('getting messages')
    session = db.get_session()
    try:
        messages = session.query(Tweet, TwitterUser) \
            .join(TwitterUser, and_(Tweet.user_id == TwitterUser.user_id, Tweet.client == TwitterUser.client)) \
            .filter(Tweet.neotter_user_id == user_id, Tweet.created_datetime >= start_time) \
            .order_by(Tweet.created_datetime) \
            .limit(count).offset(offset)
    except (OperationalError, InternalError):
        logger.error(traceback.format_exc())
    finally:
        session.close()
    result = []
    for tw, user in messages:
        message = tw.to_dict()
        message.update(user.to_dict())
        result.append(message)
    return result
