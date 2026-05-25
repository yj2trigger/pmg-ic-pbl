import hashlib
import hmac
import os

_N = 2 ** 14
_R = 8
_P = 1
_KEY_LEN = 32


def hash_password(plain: str) -> str:
    salt = os.urandom(16)
    key = hashlib.scrypt(plain.encode(), salt=salt, n=_N, r=_R, p=_P, dklen=_KEY_LEN)
    return f"scrypt${salt.hex()}${key.hex()}"


def verify_password(plain: str, stored: str) -> bool:
    if not stored.startswith("scrypt$"):
        # legacy plaintext — accepted as-is until admin changes password
        return plain == stored
    try:
        _, salt_hex, key_hex = stored.split("$")
        salt = bytes.fromhex(salt_hex)
        expected = bytes.fromhex(key_hex)
        actual = hashlib.scrypt(plain.encode(), salt=salt, n=_N, r=_R, p=_P, dklen=_KEY_LEN)
        return hmac.compare_digest(actual, expected)
    except (ValueError, IndexError):
        return False
