import logging

from aiohttp import web
from aiohttp.test_utils import (AioHTTPTestCase, make_mocked_request,
                                unittest_run_loop)
from aiommy.middlewares import (auth_middleware,
                                content_type_setter_middleware_factory, encode,
                                logging_middleware_factory,
                                permissions_middleware)
from aiommy.permissions.base import BasePermission
from aiommy.responses import JsonErrorResponse


class MiddlewareTestCase(AioHTTPTestCase):
    async def get_application(self):
        return web.Application()

    def setUp(self):
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


class AuthMiddlewareTestCase(MiddlewareTestCase):
    @classmethod
    def setUpClass(cls):
        async def handler(self, request):
            if request.user:
                return web.HTTPOk()
            return web.HTTPForbidden()
        cls.handler = handler
        cls.payload = {'id': 1}
        cls.header = {'Authorization': 'JWT ' + encode(cls.payload).decode('utf-8')}
        cls.bad_header = {'Authorization': 'JWT BAD_JWT'}

    @unittest_run_loop
    async def test_without_auth_header(self):
        handler = await auth_middleware(self.app, self.handler)
        response = await handler(self.request)
        self.assertTrue(response.status == 403)

    @unittest_run_loop
    async def test_not_jwt_auth_header(self):
        handler = await auth_middleware(self.app, self.handler)
        request = make_mocked_request('GET', '/', headers={'Authorization': 'Bearer NOT_JWT_TOKEN'})
        response = await handler(request)
        self.assertTrue(response.status == 403)

    @unittest_run_loop
    async def test_bad_token(self):
        handler = await auth_middleware(self.app, self.handler)
        request = make_mocked_request('GET', '/', headers=self.bad_header)
        response = await handler(request)
        self.assertTrue(response.status == 403)

    @unittest_run_loop
    async def test_good_token(self):
        handler = await auth_middleware(self.app, self.handler)
        request = make_mocked_request('GET', '/', headers=self.header)
        response = await handler(request)
        self.assertTrue(response.status == 200)


class LoggingMiddlewareTestCase(MiddlewareTestCase):
    ERROR_STATUS = 503

    def get_app(self):
        return web.Application()

    def setUp(self):
        super().setUp()
        self.logger_name = 'test'
        self.logger = logging.getLogger(self.logger_name)
        self.logger.http_error = lambda req, res: self.logger.error('msg')

    async def handler_raises_err(self, _):
        raise JsonErrorResponse('msg', status=self.ERROR_STATUS)

    async def handler_return_err(self, _):
        return JsonErrorResponse('msg', status=self.ERROR_STATUS)

    @unittest_run_loop
    async def test_logging_with_http_exception(self):

        middleware = logging_middleware_factory(self.logger)
        middleware_handler = await middleware(self.app, self.handler_raises_err)

        with self.assertLogs(self.logger_name, logging.ERROR):
            response = await middleware_handler(self.request)

        self.assertEqual(response.status, self.ERROR_STATUS)

    @unittest_run_loop
    async def test_not_logging_400(self):
        async def handler_raises_404(request):
            raise web.HTTPNotFound

        logger_name = 'test'

        middleware = logging_middleware_factory(logging.getLogger(logger_name))
        middleware_handler = await middleware(self.app, handler_raises_404)

        with self.assertRaises(AssertionError):
            with self.assertLogs(logger_name, logging.ERROR):
                await middleware_handler(self.request)

    @unittest_run_loop
    async def test_msg_empty(self):
        for h in [self.handler_raises_err, self.handler_return_err]:
            middleware = logging_middleware_factory(self.logger)
            middleware_handler = await middleware(self.app, h)

            response = await middleware_handler(self.request)

            self.assertIsNone(response.text)


class ContentTypeSetterMiddlewareTestCase(MiddlewareTestCase):
    content_type = 'application/json'

    async def simple_handler(self, request):
        return web.HTTPOk(content_type='text/plain')

    @unittest_run_loop
    async def test_content_type_json(self):
        self.assertNotEqual(self.request.content_type, self.content_type)

        middleware = content_type_setter_middleware_factory(self.content_type)
        middleware_handler = await middleware(self.app, self.simple_handler)
        response = await middleware_handler(self.request)
        self.assertEqual(response.content_type, self.content_type)
