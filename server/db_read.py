import sqlite3
from logging import getLogger

logger = getLogger(__name__)

db_path = 'data/db.sqlite3'


def get_connection():
    return sqlite3.connect(db_path)


def get_recent_messages(count: int=3):
    con = get_connection()
    con.row_factory = sqlite3.Row
    cur = con.cursor()

    logger.info('getting messages')
    # TODO set order by created_datetime
    sql = f"""
        select * from messages order by created_datetime desc limit {count}
    """
    cur.execute(sql)
    messages = cur.fetchall()
    con.close()
    logger.info(f'success getting {len(messages)} messages')
    return messages
