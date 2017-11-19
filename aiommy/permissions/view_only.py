from aiohttp import web

from aiommy.permissions.base import BasePermission


class ViewOnly(BasePermission):

    async def check_permission(self, request):
        if request.method == 'GET':
            return
        return web.HTTPMethodNotAllowed(request.method, ('GET', ))
