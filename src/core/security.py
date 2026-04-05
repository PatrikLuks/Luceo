import hashlib
import os
import secrets
import uuid
from datetime import UTC, datetime, timedelta

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.models.refresh_token import RefreshToken

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT
ALGORITHM = "HS256"


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(UTC) + (
        expires_delta or timedelta(hours=settings.jwt_expiration_hours)
    )
    to_encode["exp"] = expire
    return jwt.encode(to_encode, settings.jwt_secret, algorithm=ALGORITHM)


def decode_access_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.jwt_secret, algorithms=[ALGORITHM])
    except JWTError as e:
        raise ValueError("Invalid or expired token") from e


# --- Refresh tokens (SHA-256 hash for O(1) index lookup) ---


def _hash_token(raw_token: str) -> str:
    """SHA-256 hash of a refresh token — deterministic, allows index lookup."""
    return hashlib.sha256(raw_token.encode()).hexdigest()


async def create_refresh_token(user_id: uuid.UUID, db: AsyncSession) -> str:
    """Generate a secure refresh token, store its hash, return the raw token."""
    raw_token = secrets.token_urlsafe(64)
    entry = RefreshToken(
        user_id=user_id,
        token_hash=_hash_token(raw_token),
        expires_at=datetime.now(UTC)
        + timedelta(days=settings.refresh_token_expiry_days),
    )
    db.add(entry)
    return raw_token


async def verify_refresh_token(raw_token: str, db: AsyncSession) -> RefreshToken:
    """Find and validate a refresh token. Raises ValueError if invalid."""
    token_hash = _hash_token(raw_token)
    now = datetime.now(UTC)
    result = await db.execute(
        select(RefreshToken).where(
            RefreshToken.token_hash == token_hash,
            RefreshToken.revoked_at.is_(None),
            RefreshToken.expires_at > now,
        )
    )
    entry = result.scalar_one_or_none()
    if not entry:
        raise ValueError("Invalid or expired refresh token")
    return entry


async def revoke_refresh_token(token_entry: RefreshToken) -> None:
    """Revoke a refresh token (soft-delete). Caller must commit."""
    token_entry.revoked_at = datetime.now(UTC)


# AES-256-GCM field-level encryption
def _get_aes_key() -> bytes:
    key_hex = settings.encryption_key
    if len(key_hex) < 64:
        # Pad/hash short keys for dev — in production use a proper 32-byte hex key
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
