import sqlite3
from logging import getLogger

logger = getLogger(__name__)

db_path = 'data/db.sqlite3'
DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'


def get_connection():
    return sqlite3.connect(db_path)


def get_recent_messages(count: int, offset: int, start_time: str):
    con = get_connection()
    con.row_factory = sqlite3.Row
    cur = con.cursor()

    logger.info('getting messages')
    # TODO set order by created_datetime
    sql = f"""
        select * from messages
        where created_datetime >= '{start_time}'
        order by created_datetime
        limit {count} offset {offset}
    """
    cur.execute(sql)
    messages = cur.fetchall()
    con.close()
    logger.info(f'success getting {len(messages)} messages')
    return messages
