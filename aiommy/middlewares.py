import jwt
from aiohttp import web
from jwt.exceptions import DecodeError


class AnonymousUser(dict):
    def __bool__(self):
        return False

    def __str__(self):
        return 'Anonymous'


def encode(payload, secret='', algorithm='HS256'):
    return jwt.encode(payload, secret, algorithm=algorithm)


def decode(encoded, secret='', algorithms=['HS256']):
    return jwt.decode(encoded, secret, algorithms=algorithms)


def read_token(header):
    """
    read Authorization token from header
    :param header: Authorization token
    :return: decoded token such as a user payload or AnonymousUser
    """
    try:
        type, token = header.split(' ')
    except ValueError:
        return AnonymousUser()

    if type != 'JWT' or not token:
        return AnonymousUser()

    try:
        return decode(token)
    except DecodeError:
        return AnonymousUser()


async def auth_middleware(app, handler):
    async def middleware_handler(request):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            request.user = AnonymousUser()

        else:
            request.user = read_token(auth_header)

        return await handler(request)

    return middleware_handler


async def permissions_middleware(app, handler):
    async def middleware_handler(request):
        if not hasattr(handler, 'permissions'):
            return await handler(request)

        for perm in handler.permissions:
            response = await perm.check_permission(request)
            if response:
                return response

        return await handler(request)

    return middleware_handler


def logging_middeleware_factory(logger):
    async def logging_middleware(app, handler):
        async def middleware_handler(request):
            try:
                response = await handler(request)
                if response.status < 500:
                    return response

                logger.http_error(request, response)

                return web.Response(status=response.status)

            except web.HTTPException as err:
                if err.status < 500:
                    return err

                logger.http_error(request, err)
                return web.Response(status=err.status)

        return middleware_handler
    return logging_middleware


def content_type_setter_middleware_factory(content_type):
    async def content_type_setter_middleware(app, handler):
        async def middleware_handler(request):

            response = await handler(request)

            setattr(response, 'content_type', content_type)

            return response

        return middleware_handler
    return content_type_setter_middleware
