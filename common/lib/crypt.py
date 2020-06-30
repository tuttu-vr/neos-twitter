import os
from cryptography.fernet import Fernet


MESSAGE_ENCODING = 'utf-8'

if __name__ == '__main__':
    print(Fernet.generate_key().decode(MESSAGE_ENCODING))
else:
    CRYPT_KEY = os.getenv('NEOTTER_CRYPT_KEY')
    APPLICATION_ENV = os.getenv('APPLICATION_ENV', 'development')
    if not CRYPT_KEY and APPLICATION_ENV == 'production':
        raise EnvironmentError('No NEOTTER_CRYPT_KEY is set')
    elif CRYPT_KEY:
        fernet = Fernet(CRYPT_KEY.encode(MESSAGE_ENCODING))


def encrypt(message: str) -> str:
    if not CRYPT_KEY:
        return message
    mes_byte = message.encode(MESSAGE_ENCODING)
    token = fernet.encrypt(mes_byte)
    return token.decode(MESSAGE_ENCODING)


def decrypt(message_crypt: str) -> str:
    if not CRYPT_KEY:
        return message_crypt
    mes_byte = fernet.decrypt(message_crypt.encode(MESSAGE_ENCODING))
    return mes_byte.decode(MESSAGE_ENCODING)
