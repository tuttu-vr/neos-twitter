import sqlite3
import datetime
from logging import getLogger

from lib import session

logger = getLogger(__name__)

db_path = 'data/db.sqlite3'
DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'


def get_connection():
    return sqlite3.connect(db_path)


def register_user(user: dict):
    con = get_connection()
    cur = con.cursor()

    session_id = session.generate_session_id()
    user['session_id'] = session_id

    token = session.generate_token()
    user['token'] = token

    now = datetime.datetime.now()
    last_login = now.strftime(DATETIME_FORMAT)
    expired = (now + datetime.timedelta(days=14)).strftime(DATETIME_FORMAT)
    user['last_login'] = last_login
    user['expired'] = expired

    logger.info('register neotter_user')
    try:
        cur.execute("""replace into neotter_users values(
            '%(id)s',
            '%(name)s',
            '%(access_key)s',
            '%(access_secret)s',
            '%(session_id)s',
            '%(client)s',
            '%(token)s',
            '%(expired)s',
            '%(last_login)s'
        )""" % user)
    except sqlite3.OperationalError:
        logger.error('failed to put an user')
        logger.error(user)
    con.commit()
    con.close()
    logger.info('registered %s!' % user['name'])

    return session_id
