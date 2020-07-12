import re
import uuid
import secrets
import datetime
from common.lib import crypt

DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'


def generate_session_id():
    return str(uuid.uuid4())


def generate_token():
    return secrets.token_urlsafe(8)


def validate_session_id(session_id: str):
    return re.fullmatch(r'[a-zA-Z0-9\-]+', session_id)


def validate_token(token: str):
    return token and re.fullmatch(r'[a-zA-Z0-9_\.\-\~]+', token)


def generate_new_session():
    now = datetime.datetime.now()
    last_login = now.strftime(DATETIME_FORMAT)
    expired = (now + datetime.timedelta(days=14)).strftime(DATETIME_FORMAT)

    session_info = {
        'session_id': generate_session_id(),
        'token': generate_token(),
        'last_login': last_login,
        'expired': expired
    }
    return session_info
