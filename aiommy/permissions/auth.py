from aiohttp import web

from aiommy.permissions.base import BasePermission


class AuthPermission(BasePermission):
    async def check_permission(self, request):
        if hasattr(request, 'user') and request.user is not None and request.user.get('id'):
            return
        return await self.get_response()

    async def get_response(self):
        return web.HTTPUnauthorized()
