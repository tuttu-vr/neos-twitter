import uuid


def generate_session_id():
    return str(uuid.uuid4())


def generate_token():
    return str(uuid.uuid4())[:6]
