from typing import List
import traceback
from logging import getLogger

from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import OperationalError, InternalError

from twitter import User

from common.lib import db

logger = getLogger(__name__)

Base = declarative_base()


class TwitterUser(Base):
    user_id = Column(String, primary_key=True)
    name = Column(String)
    icon_url = Column(String)
    client = Column(String, default='twitter')

    __tablename__ = 'users'

    @classmethod
    def create(cls, user: User) -> "TwitterUser":
        twitter_user = TwitterUser(
            user_id = user.id_str,
            name = f'{user.name}@{user.screen_name}',
            icon_url = user.profile_image_url_https
        )

        return twitter_user

    def to_dict(self):
        _dict = {col.name: getattr(self, col.name) for col in self.__table__.columns}
        return _dict


def from_user_list(users: List[User]) -> List[TwitterUser]:
    twitter_users = list(map(lambda user: TwitterUser.create(user), users))
    return twitter_users


def add_all(users: List[User]):
    twitter_users = from_user_list(users)

    session = db.get_session()
    try:
        for user in twitter_users:
            session.merge(user)
    except (OperationalError, InternalError):
        logger.error(traceback.format_exc())
        session.rollback()
    else:
        session.commit()
    finally:
        session.close()


def get_by_id(user_id: str) -> TwitterUser:
    session = db.get_session()
    user = session.query(TwitterUser).filter(TwitterUser.user_id == user_id).first()
    return user
