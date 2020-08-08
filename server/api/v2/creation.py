from typing import List
from logging import getLogger

from lib import twitter
from common.models.neotter_user import NeotterUser

logger = getLogger(__name__)


def message(user: NeotterUser, message: str, media_list: List[str]):
    # TODO validate url
    status = twitter.post_message(user, message, media_list)
    logger.debug(status)
    if status: # TODO check status
        return 'Success', 200
    else:
        return 'Failed', 404


def like(user: NeotterUser, message_id: str):
    status = twitter.like_message(user, message_id)
    logger.debug(status)
    if status:
        return 'Success', 200
    else:
        return 'Failed', 404
