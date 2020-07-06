import argparse
from logging import basicConfig, DEBUG, INFO
from flask import Flask


class CustomFlask(Flask):
    jinja_options = Flask.jinja_options.copy()
    jinja_options.update(dict(
        block_start_string='(%',
        block_end_string='%)',
        variable_start_string='((',
        variable_end_string='))',
        comment_start_string='(#',
        comment_end_string='#)',
    ))


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
