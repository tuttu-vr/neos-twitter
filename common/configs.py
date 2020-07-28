import os
import datetime

db_path = os.getenv('NEOTTER_DB_PATH', 'data/db.sqlite3')
datetime_format = '%Y-%m-%d %H:%M:%S'
auth_expiration_date = 14

TIMEZONE_LOCAL = datetime.timezone(datetime.timedelta(hours=+9), 'JST')
TIMEZONE_UTC = datetime.timezone(datetime.timedelta(hours=+0), 'UTC')
