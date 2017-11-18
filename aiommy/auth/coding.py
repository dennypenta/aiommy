import jwt

from app import settings


def encode(payload, secret=settings.JWT_SECRET, algorithm='HS256'):
    return jwt.encode(payload, secret, algorithm=algorithm).decode('utf-8')


def decode(encoded, secret=settings.JWT_SECRET, algorithms=['HS256']):
    return jwt.decode(encoded, secret, algorithms=algorithms)
