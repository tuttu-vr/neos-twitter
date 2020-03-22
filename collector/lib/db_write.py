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


def migration():
    con = get_connection()
    cur = con.cursor()
    cur.execute("""
        create table messages(
            message_id text primary key, message text, name text, created_datetime text
        )""")
    con.commit()
    con.close()
    logger.info('table messages created')


def put_messages(messages):
    con = get_connection()
    cur = con.cursor()

    logger.info('inserting messages')
    for mes in messages:
        mes['created_datetime'] = mes['created_datetime'].strftime(DATETIME_FORMAT)
        try:
            cur.execute("""replace into messages values(
                '%(message_id)s', '%(message)s', '%(name)s', '%(created_datetime)s'
            )""" % mes)
        except sqlite3.OperationalError as e:
            logger.error('failed to put message')
            logger.error(mes)
            continue
    con.commit()
    con.close()
    logger.info(f'inserted {len(messages)} messages')


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
