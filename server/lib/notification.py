import os
import json
import requests
from logging import getLogger

logger = getLogger(__name__)
WEBHOOK_URL = os.getenv('SLACK_WEBHOOK')


def send_message(message: str):
    if not WEBHOOK_URL:
        logger.info('No webhook url is specified.')
        return
    payload = {
        'text': message
    }
    response = requests.post(WEBHOOK_URL, data=json.dumps(payload))
    logger.debug(response.text)
