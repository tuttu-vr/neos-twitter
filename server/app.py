import argparse
from logging import getLogger, DEBUG, INFO, basicConfig
from flask import Flask, request

import db_read as db

app = Flask(__name__)
logger = getLogger(__name__)


def process_messages(messages):
    # TODO process have to be into Message class
    text_list = ['%sさん: %s' % (mes['name'], mes['message']) for mes in messages]
    response = '\n'.join(text_list)
    return response


@app.route('/recent')
def get_recent():
    count = request.args.get('count', default=3, type=int)
    messages = db.get_recent_messages(count)
    response = process_messages(messages)
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
