from aiohttp import web


class BasePermission(object):
    async def check_permission(self, request):
        return

    async def get_response(self):
        return web.HTTPForbidden()
