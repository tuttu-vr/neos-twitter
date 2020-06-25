import sqlite3
import datetime
from logging import getLogger, DEBUG, StreamHandler

logger = getLogger(__name__)
logger.addHandler(StreamHandler())
logger.setLevel(DEBUG)

db_path = 'data/db.sqlite3'
DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'

table_messages = """
create table messages(
    message_id text primary key,
    message text,
    attachments text,
    user_id text,
    created_datetime text,
    client text
)
"""
table_users = """
create table users(
    user_id text primary key,
    name text,
    icon_url text,
    client text
)
"""
table_neotter_users = """
create table neotter_users(
    id text primary key,
    name text,
    access_key text,
    access_secret text,
    session_id text,
    client text,
    token text,
    expired text,
    last_login text
)
"""

def get_connection():
    return sqlite3.connect(db_path)


def migration():
    con = get_connection()
    cur = con.cursor()
    cur.execute(table_messages)
    cur.execute(table_users)
    cur.execute(table_neotter_users)
    con.commit()
    con.close()
    logger.info('tables created')


def put_messages(messages):
    con = get_connection()
    cur = con.cursor()

    logger.info('inserting messages')
    for mes in messages:
        mes['created_datetime'] = mes['created_datetime'].strftime(DATETIME_FORMAT)
        try:
            cur.execute("""replace into messages values(
                '%(message_id)s',
                '%(message)s',
                '%(attachments)s',
                '%(user_id)s',
                '%(created_datetime)s',
                '%(client)s'
            )""" % mes)
        except sqlite3.OperationalError as e:
            logger.error('failed to put a message')
            logger.error(mes)
            continue
    con.commit()
    con.close()
    logger.info(f'inserted {len(messages)} messages')


def put_user(user_list):
    con = get_connection()
    cur = con.cursor()

    logger.info('inserting users')
    for user in user_list:
        try:
            cur.execute("""replace into users values(
                '%(user_id)s',
                '%(name)s',
                '%(icon_url)s',
                '%(client)s'
            )""" % user)
        except sqlite3.OperationalError as e:
            logger.error('failed to put an user')
            logger.error(user)
            continue
    con.commit()
    con.close()
    logger.info(f'inserted {len(user)} users')


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


if __name__ == '__main__':
    migration()
