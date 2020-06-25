import os
import sys
import argparse
import datetime
from urllib.parse import quote
from logging import getLogger, DEBUG, INFO, basicConfig
from flask import Flask, request, render_template, redirect, url_for, session

import db_read as db
from lib import oauth, db_write

app = Flask(__name__)
logger = getLogger(__name__)


DELIMITER = '$'

DEFAULT_BACKTIME_MINUTES = 30

TIMEZONE_LOCAL = datetime.timezone(datetime.timedelta(hours=+9), 'JST')
TIMEZONE_UTC = datetime.timezone(datetime.timedelta(hours=+0), 'UTC')

def process_messages(messages, start_time):
    # TODO process have to be into Message class
    def process_message(mes):
        utc_time = datetime.datetime.strptime(mes['created_datetime'], db.DATETIME_FORMAT)
        local_time_str = utc_time.astimezone(TIMEZONE_LOCAL).strftime(db.DATETIME_FORMAT)
        return ';'.join([
            quote(local_time_str),
            quote(mes['name']),
            quote(mes['icon_url']),
            quote(mes['attachments']) if mes['attachments'] else '',
            quote(mes['message'])
        ])
    text_list = [process_message(mes) for mes in messages]
    response = DELIMITER.join(text_list)
    return f'{start_time}|{len(text_list)}|{response}'


@app.route('/recent')
def get_recent():
    count      = request.args.get('count', default=3, type=int)
    offset     = request.args.get('offset', default=0, type=int)
    start_time = request.args.get('start_time', default=None, type=str)
    if not start_time:
        start_time_utc = (datetime.datetime.now(TIMEZONE_UTC) - datetime.timedelta(minutes=DEFAULT_BACKTIME_MINUTES))
        start_time = start_time_utc.astimezone(TIMEZONE_LOCAL).strftime(db.DATETIME_FORMAT)
    else:
        try:
            start_time_local = datetime.datetime.strptime(start_time, db.DATETIME_FORMAT).replace(tzinfo=TIMEZONE_LOCAL)
            start_time_utc = start_time_local.astimezone(TIMEZONE_UTC)
            logger.debug(start_time_utc)
        except ValueError:
            # to avoid sql injection
            return f'error: start time format must be "{db.DATETIME_FORMAT}" but "{start_time}"'
    logger.debug(f'count={count} offset={offset} start_time={start_time}')
    messages = db.get_recent_messages(count, offset, start_time_utc.strftime(db.DATETIME_FORMAT))
    for mes in messages:
        logger.debug(mes['message'])
    response = process_messages(messages, start_time)
    return response


@app.route('/login')
def login():
    endpoint = oauth.get_authenticate_endpoint()
    return render_template('login.html', endpoint=endpoint)


@app.route('/register')
def register():
    oauth_token = request.args.get('oauth_token')
    oauth_verifier = request.args.get('oauth_verifier')
    if not oauth_token:
        return 'Invalid access'

    user_data = oauth.get_access_token(oauth_token, oauth_verifier)
    logger.debug(user_data)
    neotter_user = {
        'id': user_data['user_id'],
        'name': user_data['screen_name'],
        'access_key': user_data['oauth_token'],
        'access_secret': user_data['oauth_token_secret'],
        'client': 'twitter'
    }

    session_id = db_write.register_user(neotter_user)
    if session_id:
        session['session_id'] = session_id
        session['name'] = user_data['screen_name']
        return redirect(url_for('user_page'))
    else:
        return 'Failed to register!'


@app.route('/user-page')
def user_page():
    if 'session_id' in session:
        user = db.get_neotter_user_by_session(session['session_id'])
    else:
        user = None
    if not user:
        return redirect(url_for('login'))
    return 'Hello %s! Your token is %s!' % (user['name'], user['token'])


@app.route('/api/new-token')
def generate_neotter_token():
    return 'test'


def logging_config(debug=False):
    _format = '[%(asctime)s %(levelname)s %(name)s]: %(message)s'
    log_level = INFO if not debug else DEBUG
    basicConfig(level=log_level, format=_format)


def get_arguments():
    parser = argparse.ArgumentParser(description='This is personal twitter api.')
    parser.add_argument('--debug', action='store_true', help='enable debug mode')
    parser.add_argument('--host', default='localhost', help='specify host name')
    parser.add_argument('--port', type=int, default=80, help='specify port')
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    args = get_arguments()
    logging_config(args.debug)

    secret_key = os.getenv('FLASK_SESSION_SECRET', None)
    if not secret_key:
        logger.error('Please set FLASK_SESSION_SECRET')
        sys.exit(1)
    app.secret_key = secret_key

    app.run(port=args.port, host=args.host, debug=args.debug)
