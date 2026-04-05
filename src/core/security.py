import os
from datetime import datetime, timedelta, timezone

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from jose import JWTError, jwt
from passlib.context import CryptContext

from src.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT
ALGORITHM = "HS256"


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(hours=settings.jwt_expiration_hours)
    )
    to_encode["exp"] = expire
    return jwt.encode(to_encode, settings.jwt_secret, algorithm=ALGORITHM)


def decode_access_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.jwt_secret, algorithms=[ALGORITHM])
    except JWTError as e:
        raise ValueError("Invalid or expired token") from e


# AES-256-GCM field-level encryption
def _get_aes_key() -> bytes:
    key_hex = settings.encryption_key
    if len(key_hex) < 64:
        # Pad/hash short keys for dev — in production use a proper 32-byte hex key
        import hashlib

        key_hex = hashlib.sha256(key_hex.encode()).hexdigest()
    return bytes.fromhex(key_hex[:64])


def encrypt_field(plaintext: str) -> str:
    """Encrypt a string field using AES-256-GCM. Returns hex(nonce + ciphertext)."""
    key = _get_aes_key()
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)
    ciphertext = aesgcm.encrypt(nonce, plaintext.encode("utf-8"), None)
    return (nonce + ciphertext).hex()


def decrypt_field(encrypted_hex: str) -> str:
    """Decrypt a hex-encoded AES-256-GCM field."""
    key = _get_aes_key()
    aesgcm = AESGCM(key)
    raw = bytes.fromhex(encrypted_hex)
    nonce = raw[:12]
    ciphertext = raw[12:]
    return aesgcm.decrypt(nonce, ciphertext, None).decode("utf-8")
