import bcrypt


def get_hashed_password(plain_text_password: bytes) -> bytes:
    return bcrypt.hashpw(plain_text_password, bcrypt.gensalt())


def check_password(plain_text_password: bytes, hashed_password: bytes) -> bool:
    return bcrypt.checkpw(plain_text_password, hashed_password)
