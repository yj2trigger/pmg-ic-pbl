import pytest
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

from app.password_utils import hash_password, verify_password


def test_hash_format():
    stored = hash_password("1234")
    assert stored.startswith("scrypt$")
    parts = stored.split("$")
    assert len(parts) == 3
    assert len(parts[1]) == 32   # 16 bytes hex
    assert len(parts[2]) == 64   # 32 bytes hex


def test_verify_correct_password():
    stored = hash_password("mypassword")
    assert verify_password("mypassword", stored)


def test_verify_wrong_password():
    stored = hash_password("mypassword")
    assert not verify_password("wrongpassword", stored)


def test_unique_salts():
    h1 = hash_password("1234")
    h2 = hash_password("1234")
    assert h1 != h2


def test_legacy_plaintext_correct():
    assert verify_password("1234", "1234")


def test_legacy_plaintext_wrong():
    assert not verify_password("5678", "1234")


def test_malformed_hash_returns_false():
    assert not verify_password("1234", "scrypt$notvalidhex$also_bad")
