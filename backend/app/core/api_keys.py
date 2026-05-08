"""Helpers for server-issued API keys used by MCP clients."""

from __future__ import annotations

import hashlib
import hmac
import secrets
from dataclasses import dataclass

from app.config.settings import envs

API_KEY_PREFIX = 'sk-app-'


@dataclass(frozen=True)
class GeneratedApiKey:
    full_key: str
    key_id: str
    secret: str
    last4: str


def generate_api_key() -> GeneratedApiKey:
    key_id = secrets.token_urlsafe(9)
    secret = secrets.token_urlsafe(32)
    full_key = f'{API_KEY_PREFIX}{key_id}.{secret}'
    return GeneratedApiKey(
        full_key=full_key,
        key_id=key_id,
        secret=secret,
        last4=full_key[-4:],
    )


def derive_api_key_hash(secret: str) -> str:
    return hmac.new(
        envs.API_KEY_HASH_PEPPER.encode(),
        secret.encode(),
        hashlib.sha256,
    ).hexdigest()


def parse_api_key(api_key: str) -> tuple[str, str]:
    if not api_key.startswith(API_KEY_PREFIX):
        raise ValueError('Invalid API key')

    raw_value = api_key.removeprefix(API_KEY_PREFIX)
    key_id, separator, secret = raw_value.partition('.')
    if not separator or not key_id or not secret:
        raise ValueError('Invalid API key')
    return key_id, secret


def verify_api_key(secret: str, expected_hash: str) -> bool:
    derived_hash = derive_api_key_hash(secret)
    return hmac.compare_digest(derived_hash, expected_hash)


def mask_api_key(last4: str) -> str:
    return f'{API_KEY_PREFIX}••••{last4}'
