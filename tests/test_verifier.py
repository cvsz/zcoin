import hashlib
from app.verifier import coinflip_new, coinflip_old, hmac_sha256_hex, verify_server_seed


def test_seed_hash_and_known_vector():
    seed = "secret"
    assert verify_server_seed(seed, hashlib.sha256(seed.encode()).hexdigest())
    expected = "6436d3dff5ae18bea9f958d83d85428bd264c422e676e6e52106192415afa1b3"
    assert hmac_sha256_hex("server", "client", 1, 1) == expected
    assert coinflip_old("server", "client", 1, 1) == 0
    assert coinflip_new("server", "client", 1, 1) == 1
