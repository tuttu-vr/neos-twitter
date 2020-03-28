import argparse
import datetime
from logging import getLogger, DEBUG, INFO, basicConfig
from flask import Flask, request

import db_read as db

app = Flask(__name__)
logger = getLogger(__name__)


DELIMITER = '%&'

DEFAULT_BACKTIME_MINUTES = 30

def process_messages(messages, start_time):
    # TODO process have to be into Message class
    text_list = ['%sさん: %s' % (mes['name'], mes['message']) for mes in messages]
    response = DELIMITER.join(text_list)
    return f'{start_time}|{len(text_list)}|{response}'


@app.route('/recent')
def get_recent():
    count      = request.args.get('count', default=3, type=int)
    offset     = request.args.get('offset', default=0, type=int)
    start_time = request.args.get('start_time', default=None, type=str)
    if not start_time:
        start_time = (datetime.datetime.now() - datetime.timedelta(minutes=DEFAULT_BACKTIME_MINUTES)).strftime(db.DATETIME_FORMAT)
    else:
        try:
            datetime.datetime.strptime(start_time, db.DATETIME_FORMAT)
        except ValueError:
            # to avoid sql injection
            return f'error: start time format must be "{db.DATETIME_FORMAT}" but "{start_time}"'
    logger.debug(f'count={count} offset={offset} start_time={start_time}')
    messages = db.get_recent_messages(count, offset, start_time)
    for mes in messages:
        logger.debug(mes['message'])
    response = process_messages(messages, start_time)
    return response


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

    app.run(port=args.port, host=args.host, debug=args.debug)
