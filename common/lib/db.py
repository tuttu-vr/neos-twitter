from common import configs
import sqlite3

import sqlalchemy
import sqlalchemy.orm


db_path = configs.db_path

table_messages = """
create table messages(
    message_id text primary key,
    message text,
    attachments text,
    user_id text,
    created_datetime text,
    client text,
    neotter_user_id text
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
    last_login text,
    remote_addr text,
    enable_ip_confirm integer default 1
)
"""


def migration():
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    cur.execute(table_messages)
    cur.execute(table_users)
    cur.execute(table_neotter_users)
    con.commit()
    con.close()


def get_session():
    engine = sqlalchemy.create_engine('sqlite:///' + db_path, echo=False)
    return sqlalchemy.orm.sessionmaker(bind=engine)()


if __name__ == '__main__':
    migration()
