# ──────────────────────────────────────────────────────────────────────────────
# password_utils.py — 관리자 비밀번호 해시·검증 (scrypt)
#
# [역할]
#   hash_password(): 평문 → "scrypt$salt_hex$key_hex" 형식 문자열 반환.
#   verify_password(): 저장된 해시와 평문 비교. 타이밍 공격 방지용 hmac.compare_digest 사용.
#
# [scrypt 파라미터 선택 근거]
#   N=2^14, r=8, p=1 — 약 100ms 소요. 키오스크 환경(저전력 임베디드)에서 적절한 지연.
#   더 높이면 관리자 로그인이 체감상 느려짐.
#
# [레거시 호환]
#   저장된 비밀번호가 "scrypt$"로 시작하지 않으면 평문 비교 (초기 설정 호환).
#   main.py가 시작 시 레거시 비밀번호를 scrypt로 자동 재해시한다.
#
# [의존성]
#   이 파일을 사용하는 곳:
#     main.py → hash_password() (초기화·재해시)
#     kiosk_controller.py → verify_password() (관리자 인증)
# ──────────────────────────────────────────────────────────────────────────────

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
