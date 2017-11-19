from jwt.exceptions import DecodeError

from aiommy.auth.coding import decode


def read_token(header):
    try:
        type, token = header.split(' ')
    except ValueError:
        return None

    if type != 'JWT' or not token:
        return None

    try:
        return decode(token)
    except DecodeError:
        return None


async def auth_middleware(app, handler):
    async def middleware_handler(request):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            request.user = None

        else:
            request.user = read_token(auth_header)

        return await handler(request)

    return middleware_handler
