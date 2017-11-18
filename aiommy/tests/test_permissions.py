from aiohttp import web
from aiohttp.test_utils import unittest_run_loop, make_mocked_request

from core.middlewares import permissions_middleware
from core.permissions.base import BasePermission
from core.unittest import AioTestCase


class MiddlewareTestCase(AioTestCase):
    def setUp(self):
        self.app = web.Application()
        self.request = make_mocked_request('GET', '/')
        self.bearer_request = make_mocked_request(
            'GET',
            '/',
            headers={'Authorization': 'Bearer NOT_JWT_TOKEN'}
        )
        super().setUp()


class PermissionMiddlewareTestCase(MiddlewareTestCase):
    @classmethod
    def setUpClass(cls):
        class FailedPermission(BasePermission):
            async def check_permission(self, request):
                return await self.get_response()

        class OkPermission(BasePermission):
            async def check_permission(self, request):
                return

        async def handler_without_permission(self, request):
            return web.HTTPOk()
        cls.handler_without_permission = handler_without_permission

        async def handler_with_failed_permission(self, request):
            return web.HTTPOk()
        handler_with_failed_permission.permissions = (FailedPermission(), )
        cls.handler_with_failed_permission = handler_with_failed_permission

        async def handler_with_ok_permission(self, request):
            return web.HTTPOk()
        handler_with_ok_permission.permissions = (OkPermission(), )
        cls.handler_with_ok_permission = handler_with_ok_permission

    @unittest_run_loop
    async def test_pass_permission(self):
        handler = await permissions_middleware(self.app, self.handler_without_permission)
        response = await handler(self.request)
        self.assertTrue(response.status == 200)

    @unittest_run_loop
    async def test_failed_permission(self):
        handler = await permissions_middleware(self.app, self.handler_with_failed_permission)
        response = await handler(self.request)
        self.assertTrue(response.status == 403)

    @unittest_run_loop
    async def test_ok_permission(self):
        handler = await permissions_middleware(self.app, self.handler_with_ok_permission)
        response = await handler(self.request)
        self.assertTrue(response.status == 200)
