from __future__ import annotations

import hashlib
import hmac


def hmac_sha256_hex(server_seed: str, client_seed: str, nonce: int, round_no: int) -> str:
    message = f"{client_seed}:{nonce}:{round_no}".encode()
    return hmac.new(server_seed.encode(), message, hashlib.sha256).hexdigest()


def verify_server_seed(server_seed: str, committed_hash: str) -> bool:
    if not server_seed or not committed_hash:
        return False
    actual = hashlib.sha256(server_seed.encode()).hexdigest()
    return hmac.compare_digest(actual.lower(), committed_hash.lower())


def coinflip_old(server_seed: str, client_seed: str, nonce: int, round_no: int) -> int:
    """Historical four-byte CoinFlip verifier mapping."""
    hx = hmac_sha256_hex(server_seed, client_seed, nonce, round_no)
    b = bytes.fromhex(hx)
    u = b[0] / 256 + b[1] / (256**2) + b[2] / (256**3) + b[3] / (256**4)
    return int(u * 2)


def slide_window_number(hash_hex: str, events: int) -> float:
    index = int(hash_hex[:15], 16) % 47
    num = int(hash_hex[index:index + 14], 16) >> 3
    return num * (2 ** -53) * events


def coinflip_new(server_seed: str, client_seed: str, nonce: int, round_no: int) -> int:
    hx = hmac_sha256_hex(server_seed, client_seed, nonce, round_no)
    return int(slide_window_number(hx, 2))


def verify_result(server_seed: str, client_seed: str, nonce: int, round_no: int,
                  reported_result: int, algorithm: str = "new") -> dict:
    if algorithm not in {"old", "new"}:
        raise ValueError("algorithm must be old or new")
    fn = coinflip_new if algorithm == "new" else coinflip_old
    expected = fn(server_seed, client_seed, nonce, round_no)
    return {
        "algorithm": algorithm,
        "expected_result": expected,
        "reported_result": int(reported_result),
        "result_match": expected == int(reported_result),
        "hmac_sha256": hmac_sha256_hex(server_seed, client_seed, nonce, round_no),
    }
