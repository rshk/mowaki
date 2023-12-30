import base64
import hashlib
import hmac
import json
import os


class InvalidPassword(Exception):
    pass


SCRYPT_PARAMS = {
    "n": 2**14,
    "r": 2**4,
    "p": 1,
    "maxmem": 128 * (1024**2),  # 128 MiB
    "dklen": 64,
}


def create_encrypted_password(plaintext: str) -> str:
    salt = os.urandom(16)
    key_bytes = hashlib.scrypt(plaintext.encode("utf-8"), salt=salt, **SCRYPT_PARAMS)
    data = {
        "method": "scrypt",
        "salt": salt.hex(),
        "params": SCRYPT_PARAMS,
        "key": key_bytes.hex(),
    }
    return base64.encodebytes(json.dumps(data).encode("utf-8")).decode("utf-8")


def validate_encrypted_password(encrypted: str, plaintext: str):
    decoded = base64.decodebytes(encrypted.encode("utf-8"))
    data = json.loads(decoded)

    if data["method"] == "scrypt":
        key_bytes = bytes.fromhex(data["key"])
        salt = bytes.fromhex(data["salt"])
        params = data["params"]
        result = hashlib.scrypt(plaintext.encode("utf-8"), salt=salt, **params)
        if not hmac.compare_digest(key_bytes, result):
            raise InvalidPassword("The provided password doesn't match")
        return True

    raise ValueError(f"Unsupported password encryption method: {data['method']}")
