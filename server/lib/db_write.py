import sqlite3
import datetime
from logging import getLogger
from common import configs

logger = getLogger(__name__)

db_path = 'data/db.sqlite3'
DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'
AUTH_EXPIRATION_DATE = configs.auth_expiration_date


def get_connection():
    return sqlite3.connect(db_path)


def register_user(user: dict):
    con = get_connection()
    cur = con.cursor()

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
            '%(last_login)s',
            '%(remote_addr)s',
            1
        )""" % user)
    except sqlite3.OperationalError as e:
        logger.error('failed to put an user')
        logger.error(user)
        logger.error(e.with_traceback())
        raise ValueError('Error: failed to register!')
    con.commit()
    con.close()
    logger.info('registered %s!' % user['name'])


def update_auth_expiration(user):
    now = datetime.datetime.now()
    expired = (now + datetime.timedelta(days=AUTH_EXPIRATION_DATE)).strftime(DATETIME_FORMAT)

    sql = f"""
        update neotter_users
        set expired = '{expired}'
        where id = '{user["id"]}'
    """

    con = get_connection()
    cur = con.cursor()
    try:
        cur.execute(sql)
    except sqlite3.OperationalError as e:
        logger.error('failed to update auth expiration')
        logger.error(user)
        logger.error(e.with_traceback())
    con.commit()
    con.close()
