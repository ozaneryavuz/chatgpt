from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import time

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


def create_access_token(user_id: str) -> str:
    payload = {
        "sub": user_id,
        "exp": int(time.time()) + settings.token_ttl_seconds,
        "v": 1,
    }
    payload_bytes = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
    payload_text = _b64encode(payload_bytes)
    signature = hmac.new(
        settings.token_secret.encode("utf-8"),
        payload_text.encode("ascii"),
        hashlib.sha256,
    ).digest()
    return f"{payload_text}.{_b64encode(signature)}"


def decode_access_token(token: str) -> str:
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
        return str(payload["sub"])
    except (KeyError, ValueError, json.JSONDecodeError) as exc:
        raise ValueError("Geçersiz veya süresi dolmuş oturum.") from exc
