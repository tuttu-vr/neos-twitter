import sqlite3
from common import configs
from logging import getLogger

logger = getLogger(__name__)

db_path = configs.db_path
DATETIME_FORMAT = configs.datetime_format


def _get_connection():
    return sqlite3.connect(db_path)


def _execute_query(sql: str, values: list=None):
    con = _get_connection()
    cur = con.cursor()
    try:
        if values:
            cur.executemany(sql, values)
        else:
            cur.execute(sql)
    except (sqlite3.OperationalError, sqlite3.ProgrammingError) as e:
        logger.error('failed to execute query')
        logger.error(sql)
        logger.error(values)
        raise e
    con.commit()
    con.close()


def insert_from_dict(table_name: str, json: list):
    """
    json must be this format
    json = [
        {"col1": "value1", "col2": "value2", ...},
        {"col1": "value1", "col2": "value2", ...},
        ...
    ]
    """
    if not json:
        logger.error('no json data')
        return
    sample = json[0]
    keys = ','.join(sample.keys())
    values = [tuple(row.values()) for row in json]
    placeholder = ','.join(['?'] * len(sample.keys()))
    sql = 'insert into %s(%s) values(%s)' % (table_name, keys, placeholder)
    _execute_query(sql, values)


def get_all_data(table_name: str, order_by: str=None):
    con = _get_connection()
    # con.row_factory = sqlite3.Row
    cur = con.cursor()

    sql = f'select * from {table_name}'
    if order_by:
        sql += f' order by {order_by}'
    cur.execute(sql)
    data = cur.fetchall()
    con.close()
    return data


def delete_all_data(table_name: str):
    sql = f'delete from {table_name}'
    _execute_query(sql)
