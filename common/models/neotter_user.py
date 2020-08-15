from typing import List, Dict
import traceback
import datetime
from logging import getLogger

from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import OperationalError, InternalError

from common.lib import db, crypt, datetime_utils
from common import configs

DATETIME_FORMAT = configs.datetime_format
logger = getLogger(__name__)

Base = declarative_base()


class NeotterUser(Base):
    id = Column(String, primary_key=True)
    name = Column(String)
    access_key = Column(String)
    access_secret = Column(String)
    session_id = Column(String)
    client = Column(String, default='twitter')
    token = Column(String)
    expired = Column(String)
    last_login = Column(String)
    remote_addr = Column(String)
    enable_ip_confirm = Column(Integer)

    __tablename__ = 'neotter_users'

    def to_dict(self) -> Dict:
        _dict = {col.name: getattr(self, col.name)
                 for col in self.__table__.columns}
        return _dict

    def get_auth_token(self) -> (str, str):
        return (
            crypt.decrypt(self.access_key),
            crypt.decrypt(self.access_secret)
        )


def register(user_dict: dict):
    user = NeotterUser(**user_dict)
    session = db.get_session()
    try:
        session.add(user)
    except (OperationalError, InternalError):
        logger.error(traceback.format_exc())
        session.rollback()
        raise ValueError('Failed to register user.')
    else:
        session.commit()
    finally:
        session.close()


def delete_expired_users():
    current = datetime.datetime.utcnow().strftime(DATETIME_FORMAT)
    session = db.get_session()
    try:
        session.query(NeotterUser).filter(
            NeotterUser.expired <= current).delete()
    except (OperationalError, InternalError):
        logger.error(traceback.format_exc())
        session.rollback()
    else:
        session.commit()
    finally:
        session.close()


def get_valid_users() -> List[NeotterUser]:
    current = datetime.datetime.utcnow().strftime(DATETIME_FORMAT)
    session = db.get_session()
    users = list(map(
        lambda user: user.to_dict(),
        session.query(NeotterUser).filter(NeotterUser.expired >= current)))
    session.close()
    return users


def get_by_token(token: str) -> NeotterUser:
    current = datetime.datetime.utcnow().strftime(DATETIME_FORMAT)
    session = db.get_session()
    user = session.query(NeotterUser).filter(
        NeotterUser.token == token,
        NeotterUser.expired >= current).first()
    session.close()
    return user


def get_by_session(session_id: str) -> NeotterUser:
    session = db.get_session()
    user = session.query(NeotterUser).filter(
        NeotterUser.session_id == session_id).first()
    session.close()
    return user


def extend_expiration(user_id: str):
    session = db.get_session()
    user = session.query(NeotterUser).filter(
        NeotterUser.id == user_id).first()
    new_expired = datetime_utils.day_after(configs.auth_expiration_date)
    user.expired = datetime_utils.datetime_to_neotter_inner(new_expired)
    session.commit()
    session.close()
