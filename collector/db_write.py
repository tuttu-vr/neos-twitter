import sqlite3
from logging import getLogger, DEBUG, StreamHandler

logger = getLogger(__name__)
logger.addHandler(StreamHandler())
logger.setLevel(DEBUG)

db_path = 'data/db.sqlite3'


def get_connection():
    return sqlite3.connect(db_path)


def migration():
    con = get_connection()
    cur = con.cursor()
    cur.execute("""
        create table messages(
            message_id text primary key, message text, name text, created_datetime text
        )""")


def put_messages(messages):
    con = get_connection()
    cur = con.cursor()

    logger.info('inserting messages')
    for mes in messages:
        cur.execute("""replace into messages values(
            '%(message_id)s', '%(message)s', '%(name)s', '%(created_datetime)s'
        )""" % mes)
    con.commit()
    con.close()
    logger.info(f'inserted {len(messages)} messages')


if __name__ == '__main__':
    migration()
