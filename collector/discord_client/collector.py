import os
import urllib.parse
import sqlite3
import time
import datetime
from logging import getLogger, DEBUG, StreamHandler

from dotenv import load_dotenv
import discord as dc

import lib.db_write as db

logger = getLogger(__name__)
logger.addHandler(StreamHandler())
logger.setLevel(DEBUG)

load_dotenv(verbose=True)

ACCESS_TOKEN = os.getenv('DISCORD_TOKEN', '')

DATETIME_FORMAT = '%a %b %d %H:%M:%S %z %Y'
INITIAL_GET_NUM = 0

client = dc.Client()
channel_id = 675948567826923520
# channel_id = 683269734443384858 # private test
# channel_id = 679153526395502592 # welcome event
# channel_id = 683869905933959227 # flyers 連絡用


@client.event
async def on_ready():
    channel = client.get_channel(channel_id)
    logger.info(f'Channel: {channel.name}')
    messages = await channel.history(limit=INITIAL_GET_NUM).flatten()
    store_timeline(list(reversed(messages)))


@client.event
async def on_message(message):
    if message.channel.id != channel_id:
        return
    store_timeline([message])


def debug_timeline(timeline):
    logger.debug(timeline)
    for tweet in timeline:
        display = '%s | (%s) %s: %s' % (tweet.created_at, tweet.id, tweet.author.name, extract_message(tweet))
        logger.debug(display)
        if tweet.application:
            logger.debug(tweet.application)


def extract_message(message):
    mes = message.content
    if message.application:
        mes += ' ' + message.application['description']
    for embed in message.embeds:
        mes += f' [{embed.title}]{embed.description}'
    for attachment in message.attachments:
        mes += ';;;' + attachment.url
    return mes


def timeline_to_dict_iter(timeline):
    return map(lambda t: {
        'message_id': t.id,
        'message': extract_message(t),
        'name': t.author.name,
        'created_datetime': t.created_at
    }, timeline)


def pipeline(timeline_iter):
    timeline_list = list(timeline_iter)
    for tw in timeline_list:
        tw['message'] = ' '.join(tw['message'].splitlines())
    return timeline_list


def store_timeline(timeline):
    logger.debug(f'Got {len(timeline)} messages')
    if len(timeline) == 0:
        return
    timeline_iter = timeline_to_dict_iter(timeline)
    timeline_list = pipeline(timeline_iter)
    db.put_messages(timeline_list)


def main():
    client.run(ACCESS_TOKEN)


if __name__ == '__main__':
    main()
