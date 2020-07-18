from common import configs
from common.lib import db
import sqlite3
import datetime
from logging import getLogger, DEBUG, StreamHandler

logger = getLogger(__name__)
logger.addHandler(StreamHandler())
logger.setLevel(DEBUG)

db_path = configs.db_path
DATETIME_FORMAT = configs.datetime_format


def get_connection():
    return sqlite3.connect(db_path)


def delete_old_messages(hour_before: int=48):
    con = get_connection()
    cur = con.cursor()

    delete_from = (datetime.datetime.now() - datetime.timedelta(hours=hour_before)).strftime(DATETIME_FORMAT)
    sql = f"""
        %s from messages
        where created_datetime <= '{delete_from}'
    """
    cur.execute(sql % 'select count(*)')
    count = cur.fetchone()[0]
    logger.info(f'deleting {count} messages')
    cur.execute(sql % 'delete')
    con.commit()
    con.close()


def delete_expired_users():
    con = get_connection()
    cur = con.cursor()

    now = datetime.datetime.now().strftime(DATETIME_FORMAT)
    sql = f"""
        %s from neotter_users
        where expired < '{now}'
    """
    cur.execute(sql % 'select count(*)')
    count = cur.fetchone()[0]
    if count > 0:
        logger.info(f'deleting {count} users')
        cur.execute(sql % 'delete')
        con.commit()
    con.close()


if __name__ == '__main__':
    db.migration()
