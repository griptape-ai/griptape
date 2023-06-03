import hashlib


def str_to_hash(text: str, hash_algorithm: str = "sha256") -> str:
    m = hashlib.new(hash_algorithm)

    m.update(text.encode())

    return m.hexdigest()
