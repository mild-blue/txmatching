from txmatching.auth.crypto import bcrypt


def encode_password(password: str) -> str:
    """
    Encodes password to hash.
    """
    return bcrypt.generate_password_hash(password).decode()


def password_matches_hash(password_hash: str, password: str) -> bool:
    """
    Validates that password_hash and password are the same.
    """
    return bcrypt.check_password_hash(password_hash, password)
