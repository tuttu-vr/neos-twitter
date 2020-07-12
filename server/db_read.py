import sqlite3
import datetime
from logging import getLogger
from lib.settings import DATETIME_FORMAT

logger = getLogger(__name__)

db_path = 'data/db.sqlite3'
DATETIME_FORMAT = DATETIME_FORMAT


def get_connection():
    return sqlite3.connect(db_path)


def _get_data(sql: str):
    con = get_connection()
    con.row_factory = sqlite3.Row
    cur = con.cursor()

    cur.execute(sql)
    data = cur.fetchall()
    con.close()
    return data


def get_recent_messages(count: int, offset: int, start_time: str, user_id: str):
    logger.info('getting messages')
    sql = f"""
        select
            mes.message, mes.attachments, mes.created_datetime,
            us.name, us.icon_url
        from messages as mes
        left join users as us using(user_id, client)
        where
            mes.created_datetime >= '{start_time}'
            and mes.neotter_user_id = '{user_id}'
        order by mes.created_datetime
        limit {count} offset {offset}
    """
    messages = _get_data(sql)
    logger.info(f'success getting {len(messages)} messages')
    return messages


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
