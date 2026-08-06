import base64
from cryptography.fernet import Fernet
from app.config import settings


def _get_fernet() -> Fernet:
    key = settings.ENCRYPTION_KEY
    if len(key) != 44:
        key = base64.urlsafe_b64encode(key.zfill(32).encode()[:32]).decode()
    return Fernet(key.encode())


def encrypt_token(plain_token: str) -> str:
    if not plain_token:
        return ""
    f = _get_fernet()
    return f.encrypt(plain_token.encode()).decode()


def decrypt_token(encrypted_token: str) -> str:
    if not encrypted_token:
        return ""
    f = _get_fernet()
    return f.decrypt(encrypted_token.encode()).decode()
