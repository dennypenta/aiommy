from jwt.exceptions import DecodeError

from aiommy.auth.coding import decode


def read_token(header, secret):
    try:
        type, token = header.split(' ')
    except ValueError:
        return None

    if type != 'JWT' or not token:
        return None

    try:
        return decode(token, secret)
    except DecodeError:
        return None


def auth_middleware_factory(secret):
    async def auth_middleware(app, handler):
        async def middleware_handler(request):
            auth_header = request.headers.get('Authorization')
            if not auth_header:
                request.user = None

            else:
                request.user = read_token(auth_header, secret)

            return await handler(request)

        return middleware_handler
    return auth_middleware
