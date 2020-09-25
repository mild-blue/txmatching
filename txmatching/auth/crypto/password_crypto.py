from txmatching.auth.crypto import bcrypt


def encode_password(password: str) -> str:
    """
    Encodes password to hash.
    """
    return bcrypt.generate_password_hash(password).decode()


def password_matches_hash(pwd_hash: str, password: str) -> bool:
    """
    Validates that password hash and password are same.
    """
    return bcrypt.check_password_hash(pwd_hash, password)
