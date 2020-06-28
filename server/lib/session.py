import re
import uuid


def generate_session_id():
    return str(uuid.uuid4())


def generate_token():
    return str(uuid.uuid4())[:8]


def validate_token(token: str):
    return re.fullmatch(r'[a-zA-Z0-9]+', token)
