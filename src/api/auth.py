from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import time
from dataclasses import dataclass


JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret")
JWT_TTL_SECONDS = int(os.getenv("JWT_TTL_SECONDS", "86400"))


@dataclass
class AuthUser:
    id: int
    tg_user_id: int
    role: str


def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode().rstrip("=")


def _b64url_decode(data: str) -> bytes:
    pad = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + pad)


def create_jwt(payload: dict) -> str:
    header = {"alg": "HS256", "typ": "JWT"}
    full_payload = {**payload, "exp": int(time.time()) + JWT_TTL_SECONDS}
    h = _b64url_encode(json.dumps(header, separators=(",", ":")).encode())
    p = _b64url_encode(json.dumps(full_payload, separators=(",", ":")).encode())
    signing_input = f"{h}.{p}".encode()
    sig = hmac.new(JWT_SECRET.encode(), signing_input, hashlib.sha256).digest()
    return f"{h}.{p}.{_b64url_encode(sig)}"


def verify_jwt(token: str) -> dict:
    try:
        h, p, s = token.split(".")
    except ValueError as exc:
        raise ValueError("invalid token") from exc
    signing_input = f"{h}.{p}".encode()
    expected = hmac.new(JWT_SECRET.encode(), signing_input, hashlib.sha256).digest()
    got = _b64url_decode(s)
    if not hmac.compare_digest(expected, got):
        raise ValueError("invalid signature")
    payload = json.loads(_b64url_decode(p))
    if int(payload.get("exp", 0)) < int(time.time()):
        raise ValueError("token expired")
    return payload


def verify_telegram_login(data: dict, bot_token: str) -> bool:
    check_hash = data.get("hash")
    if not check_hash:
        return False
    fields = {k: v for k, v in data.items() if k != "hash" and v is not None}
    data_check_string = "\n".join(f"{k}={fields[k]}" for k in sorted(fields.keys()))
    secret = hashlib.sha256(bot_token.encode()).digest()
    calc = hmac.new(secret, data_check_string.encode(), hashlib.sha256).hexdigest()
    return hmac.compare_digest(calc, str(check_hash))
