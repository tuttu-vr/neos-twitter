from typing import List
import traceback
import datetime
from logging import getLogger

from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import OperationalError, InternalError

from common.lib import db
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

    def to_dict(self):
        _dict = {col.name: getattr(self, col.name) for col in self.__table__.columns}
        return _dict


def delete_expired_users():
    current = datetime.datetime.utcnow().strftime(DATETIME_FORMAT)
    session = db.get_session()
    try:
        session.query(NeotterUser).filter(NeotterUser.expired <= current).delete()
    except (OperationalError, InternalError):
        logger.error(traceback.format_exc())
        session.rollback()
    else:
        session.commit()
    finally:
        session.close()


def get_valid_users():
    current = datetime.datetime.utcnow().strftime(DATETIME_FORMAT)
    session = db.get_session()
    users = list(map(
        lambda user: user.to_dict(),
        session.query(NeotterUser).filter(NeotterUser.expired >= current)))
    session.close()
    return users
