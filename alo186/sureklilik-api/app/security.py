from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import secrets
import struct
import time
from datetime import datetime, timezone
from urllib.parse import quote

from cryptography.fernet import Fernet, InvalidToken

from .config import settings


def _b64encode(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode("ascii")


def _b64decode(value: str) -> bytes:
    return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))


def hash_password(password: str) -> str:
    salt = os.urandom(16)
    derived = hashlib.scrypt(
        password.encode("utf-8"),
        salt=salt,
        n=2**14,
        r=8,
        p=1,
        dklen=32,
    )
    return f"scrypt${_b64encode(salt)}${_b64encode(derived)}"


def verify_password(password: str, encoded: str) -> bool:
    try:
        scheme, salt_text, expected_text = encoded.split("$", 2)
        if scheme != "scrypt":
            return False
        derived = hashlib.scrypt(
            password.encode("utf-8"),
            salt=_b64decode(salt_text),
            n=2**14,
            r=8,
            p=1,
            dklen=32,
        )
        return hmac.compare_digest(derived, _b64decode(expected_text))
    except (ValueError, TypeError):
        return False


def create_access_token(
    user_id: str,
    *,
    session_id: str,
    token_version: int,
    expires_at: datetime | None = None,
) -> str:
    expiration = expires_at or datetime.fromtimestamp(
        int(time.time()) + settings.token_ttl_seconds,
        tz=timezone.utc,
    )
    payload = {
        "sub": user_id,
        "exp": int(expiration.timestamp()),
        "jti": session_id,
        "ver": int(token_version),
        "v": 2,
    }
    payload_bytes = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
    payload_text = _b64encode(payload_bytes)
    signature = hmac.new(
        settings.token_secret.encode("utf-8"),
        payload_text.encode("ascii"),
        hashlib.sha256,
    ).digest()
    return f"{payload_text}.{_b64encode(signature)}"


def decode_access_token(token: str) -> dict[str, object]:
    try:
        payload_text, signature_text = token.split(".", 1)
        expected = hmac.new(
            settings.token_secret.encode("utf-8"),
            payload_text.encode("ascii"),
            hashlib.sha256,
        ).digest()
        if not hmac.compare_digest(expected, _b64decode(signature_text)):
            raise ValueError("Geçersiz imza.")
        payload = json.loads(_b64decode(payload_text))
        if int(payload["exp"]) < int(time.time()):
            raise ValueError("Oturum süresi doldu.")
        if not payload.get("sub") or not payload.get("jti"):
            raise ValueError("Eksik oturum alanı.")
        return payload
    except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
        raise ValueError("Geçersiz veya süresi dolmuş oturum.") from exc


def create_one_time_token() -> str:
    return secrets.token_urlsafe(32)


def hash_one_time_token(token: str) -> str:
    return hmac.new(
        settings.token_secret.encode("utf-8"),
        token.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


def hash_client_value(value: str | None) -> str | None:
    if not value:
        return None
    return hmac.new(
        settings.token_secret.encode("utf-8"),
        value.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


def encrypt_secret(value: str) -> str:
    return Fernet(settings.data_encryption_key.encode("ascii")).encrypt(value.encode("utf-8")).decode("ascii")


def decrypt_secret(value: str) -> str:
    try:
        return Fernet(settings.data_encryption_key.encode("ascii")).decrypt(value.encode("ascii")).decode("utf-8")
    except InvalidToken as exc:
        raise ValueError("Şifreli güvenlik verisi çözülemedi.") from exc


def generate_totp_secret() -> str:
    return base64.b32encode(os.urandom(20)).decode("ascii").rstrip("=")


def _decode_base32(value: str) -> bytes:
    cleaned = value.strip().replace(" ", "").upper()
    return base64.b32decode(cleaned + "=" * (-len(cleaned) % 8), casefold=True)


def totp_code(secret: str, *, timestamp: int | None = None, period: int = 30, digits: int = 6) -> str:
    current = int(time.time()) if timestamp is None else int(timestamp)
    counter = current // period
    digest = hmac.new(_decode_base32(secret), struct.pack(">Q", counter), hashlib.sha1).digest()
    offset = digest[-1] & 0x0F
    number = (struct.unpack(">I", digest[offset : offset + 4])[0] & 0x7FFFFFFF) % (10**digits)
    return str(number).zfill(digits)


def verify_totp(code: str, secret: str, *, timestamp: int | None = None, window: int = 1) -> bool:
    normalized = "".join(ch for ch in str(code) if ch.isdigit())
    if len(normalized) != 6:
        return False
    current = int(time.time()) if timestamp is None else int(timestamp)
    return any(
        hmac.compare_digest(normalized, totp_code(secret, timestamp=current + offset * 30))
        for offset in range(-window, window + 1)
    )


def totp_provisioning_uri(secret: str, email: str, issuer: str = "ALO186") -> str:
    label = quote(f"{issuer}:{email}")
    return f"otpauth://totp/{label}?secret={quote(secret)}&issuer={quote(issuer)}&algorithm=SHA1&digits=6&period=30"


def generate_recovery_codes(count: int = 8) -> list[str]:
    return [f"{secrets.token_hex(2).upper()}-{secrets.token_hex(2).upper()}" for _ in range(count)]


def hash_recovery_code(code: str) -> str:
    normalized = code.replace("-", "").replace(" ", "").upper()
    return hmac.new(
        settings.token_secret.encode("utf-8"),
        normalized.encode("ascii"),
        hashlib.sha256,
    ).hexdigest()


def consume_recovery_code(code: str, encoded_codes_json: str | None) -> tuple[bool, str | None]:
    if not encoded_codes_json:
        return False, encoded_codes_json
    try:
        hashes = json.loads(encoded_codes_json)
    except json.JSONDecodeError:
        return False, encoded_codes_json
    candidate = hash_recovery_code(code)
    for index, item in enumerate(hashes):
        if hmac.compare_digest(str(item), candidate):
            del hashes[index]
            return True, json.dumps(hashes, separators=(",", ":"))
    return False, encoded_codes_json
