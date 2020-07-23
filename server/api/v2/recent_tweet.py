from typing import List, Dict
import datetime
import traceback
from urllib.parse import quote
from logging import getLogger

from lib.settings import TWEET_DELIMITER, DATETIME_FORMAT

logger = getLogger(__name__)

DELIMITER = TWEET_DELIMITER

TIMEZONE_LOCAL = datetime.timezone(datetime.timedelta(hours=+9), 'JST')
TIMEZONE_UTC = datetime.timezone(datetime.timedelta(hours=+0), 'UTC')


def process_messages(messages: List[Dict], start_time: str):
    def process_message(mes):
        utc_time = datetime.datetime.strptime(mes['created_datetime'], DATETIME_FORMAT).replace(tzinfo=TIMEZONE_UTC)
        local_time_str = utc_time.astimezone(TIMEZONE_LOCAL).strftime(DATETIME_FORMAT)
        try:
            return ';'.join([
                'id=' + mes['message_id'].split('-')[1], # TODO keep original id in DB
                'created_at=' + quote(local_time_str),
                'name=' + quote(mes['name']),
                'icon_url=' + quote(mes['icon_url']),
                'attachments=' + (quote(mes['attachments']) if mes['attachments'] else ''),
                'message=' + mes['message'],
                'favorite_count=%d' % mes['favorite_count'],
                'retweet_count=%d' % mes['retweet_count'],
                'favorited=' + str(mes['favorited']),
                'retweeted=' + str(mes['retweeted'])
            ])
        except TypeError:
            logger.error(traceback.format_exc())
            for key in mes.keys():
                logger.error('%s=%s' % (key, str(mes[key])))
            return None
    text_list = list(filter(lambda x: x, [process_message(mes) for mes in messages]))
    response = DELIMITER.join(text_list)
    return f'{start_time}|{len(text_list)}|{response}'
