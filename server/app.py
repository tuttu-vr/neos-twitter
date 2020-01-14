import argparse
import datetime
from logging import getLogger, DEBUG, INFO, basicConfig
from flask import Flask, request

import db_read as db

app = Flask(__name__)
logger = getLogger(__name__)


def process_messages(messages, start_time):
    # TODO process have to be into Message class
    text_list = ['%sさん[%s]: %s' % (mes['name'], mes['created_datetime'], mes['message']) for mes in messages]
    response = '\n'.join(text_list)
    return start_time + '|' + response


@app.route('/recent')
def get_recent():
    count      = request.args.get('count', default=3, type=int)
    offset     = request.args.get('offset', default=0, type=int)
    start_time = request.args.get('start_time', default=None, type=str)
    if start_time is None:
        start_time = (datetime.datetime.now() - datetime.timedelta(minutes=30)).strftime(db.DATETIME_FORMAT)
    logger.debug(f'count={count} offset={offset} start_time={start_time}')
    messages = db.get_recent_messages(count, offset, start_time)
    response = process_messages(messages, start_time)
    return response


def logging_config(debug=False):
    _format = '[%(asctime)s %(levelname)s %(name)s]: %(message)s'
    log_level = INFO if not debug else DEBUG
    basicConfig(level=log_level, format=_format)


def get_arguments():
    parser = argparse.ArgumentParser(description='This is personal twitter api.')
    parser.add_argument('--debug', action='store_true', help='enable debug mode')
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    args = get_arguments()
    logging_config(args.debug)

    app.run(port=80, debug=args.debug)
