import sqlite3
import datetime
from logging import getLogger
from common import configs
from lib.settings import DATETIME_FORMAT

logger = getLogger(__name__)

DB_PATH = configs.db_path
DATETIME_FORMAT = DATETIME_FORMAT


def get_connection():
    return sqlite3.connect(DB_PATH)


def _get_data(sql: str):
    con = get_connection()
    con.row_factory = sqlite3.Row
    cur = con.cursor()

    cur.execute(sql)
    data = cur.fetchall()
    con.close()
    return data


def get_neotter_user_by_session(session_id: str):
    logger.info('getting neotter user')
    sql = """
        select *
        from neotter_users
        where session_id = '%s'
    """ % session_id
    result = _get_data(sql)

    return None if len(result) == 0 else result[0]


def get_neotter_user_by_token(token: str):
    logger.info('getting neotter user by token')
    sql = """
        select *
        from neotter_users
        where
            token = '%s'
        and
            expired >= '%s'
    """ % (token, datetime.datetime.now().strftime(DATETIME_FORMAT))
    result = _get_data(sql)

    return None if len(result) == 0 else result[0]
