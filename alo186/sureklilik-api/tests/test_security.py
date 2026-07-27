from __future__ import annotations

from datetime import timedelta

import pytest

from app.models import utcnow
from app.security import (
    consume_recovery_code,
    create_access_token,
    create_one_time_token,
    decode_access_token,
    decrypt_secret,
    encrypt_secret,
    generate_recovery_codes,
    generate_totp_secret,
    hash_one_time_token,
    hash_password,
    hash_recovery_code,
    totp_code,
    verify_password,
    verify_totp,
)


def test_password_token_encryption_and_totp_primitives():
    encoded = hash_password("Guvenli-Parola-2026")
    assert encoded.startswith("scrypt$")
    assert verify_password("Guvenli-Parola-2026", encoded)
    assert not verify_password("yanlis", encoded)

    ciphertext = encrypt_secret("çok gizli değer")
    assert "çok gizli değer" not in ciphertext
    assert decrypt_secret(ciphertext) == "çok gizli değer"

    session_id = "session-test-id"
    token = create_access_token(
        "user-test-id",
        session_id=session_id,
        token_version=3,
        expires_at=utcnow() + timedelta(minutes=5),
    )
    payload = decode_access_token(token)
    assert payload["sub"] == "user-test-id"
    assert payload["jti"] == session_id
    assert payload["ver"] == 3

    with pytest.raises(ValueError):
        decode_access_token(token + "bozuk")

    raw = create_one_time_token()
    assert len(raw) >= 40
    assert hash_one_time_token(raw) == hash_one_time_token(raw)
    assert hash_one_time_token(raw) != hash_one_time_token(raw + "x")

    timestamp = 1_722_000_000
    secret = generate_totp_secret()
    code = totp_code(secret, timestamp=timestamp)
    assert len(code) == 6
    assert verify_totp(code, secret, timestamp=timestamp)
    assert verify_totp(code, secret, timestamp=timestamp + 30, window=1)
    assert not verify_totp("000000" if code != "000000" else "111111", secret, timestamp=timestamp)


def test_recovery_codes_are_single_use():
    codes = generate_recovery_codes(4)
    encoded = __import__("json").dumps([hash_recovery_code(code) for code in codes])
    valid, remaining = consume_recovery_code(codes[0], encoded)
    assert valid
    assert remaining is not None
    valid_again, _ = consume_recovery_code(codes[0], remaining)
    assert not valid_again
    second_valid, _ = consume_recovery_code(codes[1].lower(), remaining)
    assert second_valid
