import os
import urllib.parse
import sqlite3
import time
import datetime
from logging import getLogger, DEBUG, StreamHandler

from dotenv import load_dotenv
import discord as dc

import db_write as db

logger = getLogger(__name__)
logger.addHandler(StreamHandler())
logger.setLevel(DEBUG)

load_dotenv(verbose=True)

ACCESS_TOKEN = os.getenv('DISCORD_TOKEN', '')

DATETIME_FORMAT = '%a %b %d %H:%M:%S %z %Y'


client = discord.Client()


@client.event
async def on_ready():
    messages = await channel.history(limit=100).flatten()
    store_timeline(messages)
    debug_timeline


@client.event
async def on_message(message):
    store_timeline([message])


def debug_timeline(timeline):
    logger.debug(timeline)
    for tweet in timeline:
        display = '%s | (%s) %s: %s' % (tweet.created_at, tweet.id, tweet.user.screen_name, tweet.text)
        logger.debug(display)


def timeline_to_dict_iter(timeline):
    return map(lambda t: {
        'message_id': t.id,
        'message': t.content,
        'name': t.author.name,
        'created_datetime': t.created_at
    }, timeline)


def pipeline(timeline_iter):
    for tw in timeline_iter:
        tw['message'] = tw['message'].replace('\n', ' ')
    return rt_removed


def store_timeline(timeline):
    logger.debug(f'Got {len(timeline)} messages')
    timeline_iter = timeline_to_dict_iter(timeline)
    timeline_list = pipeline(timeline_iter)
    db.put_messages(timeline_list)


if __name__ == '__main__':
    main()
