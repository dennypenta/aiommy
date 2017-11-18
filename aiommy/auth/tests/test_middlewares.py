from aiohttp.test_utils import unittest_run_loop, \
    make_mocked_request
from aiohttp import web

from core.unittest import AioTestCase
from auth.middlewares import auth_middleware
from auth.coding import encode


class MiddlewareTestCase(AioTestCase):
    def setUp(self):
        super().setUp()
        self.app = web.Application()
        self.request = make_mocked_request('GET', '/')
        self.bearer_request = make_mocked_request(
            'GET',
            '/',
            headers={'Authorization': 'Bearer NOT_JWT_TOKEN'})


class AuthMiddlewareTestCase(MiddlewareTestCase):
    @classmethod
    def setUpClass(cls):
        async def handler(self, request):
            if request.user:
                return web.HTTPOk()
            return web.HTTPForbidden()
        cls.handler = handler
        cls.payload = {'id': 1}
        cls.header = {'Authorization': 'JWT ' + encode(cls.payload)}
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
