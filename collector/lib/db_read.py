import sqlite3
import datetime
from logging import getLogger, DEBUG, StreamHandler

logger = getLogger(__name__)
logger.addHandler(StreamHandler())
logger.setLevel(DEBUG)

db_path = 'data/db.sqlite3'
DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'


def get_connection():
    return sqlite3.connect(db_path)


def _get_data(sql):
    con = get_connection()
    con.row_factory = sqlite3.Row
    cur = con.cursor()

    cur.execute(sql)
    data = cur.fetchall()
    con.close()
    return data


def _get_single_data(sql):
    result = _get_data(sql)
    return None if len(result) == 0 else result[0]


def get_valid_neotter_users():
    sql = """
        select *
        from neotter_users
        where expired >= '%s'
    """ % datetime.datetime.now().strftime(DATETIME_FORMAT)
    users = _get_data(sql)
    return users
