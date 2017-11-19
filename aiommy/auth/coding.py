import jwt


def encode(payload, secret='', algorithm='HS256'):
    return jwt.encode(payload, secret, algorithm=algorithm).decode('utf-8')


def decode(encoded, secret='', algorithms=['HS256']):
    return jwt.decode(encoded, secret, algorithms=algorithms)
