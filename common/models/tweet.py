from typing import List
import datetime
from urllib.parse import quote
import traceback
from logging import getLogger

from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import OperationalError, InternalError

from twitter import Status

from common import configs
from common.lib import db

logger = getLogger(__name__)

Base = declarative_base()

TWITTER_DATETIME_FORMAT = '%a %b %d %H:%M:%S %z %Y'
INNER_DATETIME_FORMAT = configs.datetime_format


class Tweet(Base):
    message_id = Column(String, primary_key=True)
    message = Column(String)
    attachments = Column(String, default='')
    user_id = Column(String)
    created_datetime = Column(String)
    client = Column(String, default='twitter')
    neotter_user_id = Column(String)
    favorite_count = Column(Integer, default=0)
    retweet_count = Column(Integer, default=0)
    favorited = Column(Boolean, default=False)
    retweeted = Column(Boolean, default=False)

    __tablename__ = 'messages'

    @classmethod
    def create(cls, status: Status, neotter_user_id: str):
        # deprecated process / TODO: remove
        if not cls.deprecated_filters(status):
            return None
        created_at = datetime.datetime.strptime(
            status.created_at, TWITTER_DATETIME_FORMAT
        ).strftime(INNER_DATETIME_FORMAT)

        tweet = Tweet(
            message_id = f'{neotter_user_id}-{status.id}',
            message = quote(status.text),
            user_id = status.user.id_str,
            created_datetime = created_at,
            neotter_user_id = neotter_user_id,
            favorite_count = status.favorite_count,
            retweet_count = status.retweeted,
            favorited = status.favorited,
            retweeted = status.retweeted
        )

        if status.media:
            tweet.attachments = ','.join(map(
                lambda m: m.media_url_https, filter(
                    lambda m: m.type=='photo', status.media)))

        return tweet

    @classmethod
    def deprecated_filters(cls, status: Status):
        return not status.text.startswith('RT ')


def from_status_list(status_list: List[Status], neotter_user_id: str):
    tweet_list = list(filter(lambda tw: tw, map(
        lambda tweet: Tweet.create(tweet, neotter_user_id), status_list)))
    return tweet_list


def extract_unique_users(status_list: List[Status]):
    uniques = {}
    for status in status_list:
        user = status.user
        uniques[user.id_str] = user
    return list(uniques.values())


def add_all(status_list: List[Status], neotter_user_id: str):
    tweet_list = from_status_list(status_list, neotter_user_id)
    session = db.get_session()
    try:
        for tweet in tweet_list:
            session.merge(tweet)
    except (OperationalError, InternalError):
        logger.error(traceback.format_exc())
        session.rollback()
    else:
        session.commit()
    finally:
        session.close()


def delete_old_tweets(hour_before: int):
    delete_from = (datetime.datetime.now() - datetime.timedelta(hours=hour_before)) \
        .strftime(INNER_DATETIME_FORMAT)
    session = db.get_session()
    try:
        session.query(Tweet).filter(Tweet.created_datetime <= delete_from).delete()
    except (OperationalError, InternalError):
        logger.error(traceback.format_exc())
        session.rollback()
    else:
        session.commit()
    finally:
        session.close()
