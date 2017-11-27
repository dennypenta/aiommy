from aiohttp import web
from aiohttp.test_utils import make_mocked_request, unittest_run_loop
from aiommy.auth.coding import encode
from aiommy.auth.middlewares import auth_middleware_factory
from aiommy.testing import AioTestCase


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
    def setUp(self):
        super().setUp()

        async def handler(request):
            if request.user:
                return web.HTTPOk()
            return web.HTTPForbidden()
        secret = 'secret'

        self.handler = handler
        self.auth_middleware = auth_middleware_factory(secret)
        self.payload = {'id': 1}
        self.header = {'Authorization': 'JWT ' + encode(self.payload, secret)}
        self.bad_header = {'Authorization': 'JWT BAD_JWT'}

    @unittest_run_loop
    async def test_without_auth_header(self):
        handler = await self.auth_middleware(self.app, self.handler)
        response = await handler(self.request)
        self.assertTrue(response.status == 403)

    @unittest_run_loop
    async def test_not_jwt_auth_header(self):
        handler = await self.auth_middleware(self.app, self.handler)
        request = make_mocked_request('GET', '/', headers={'Authorization': 'Bearer NOT_JWT_TOKEN'})
        response = await handler(request)
        self.assertTrue(response.status == 403)

    @unittest_run_loop
    async def test_bad_token(self):
        handler = await self.auth_middleware(self.app, self.handler)
        request = make_mocked_request('GET', '/', headers=self.bad_header)
        response = await handler(request)
        self.assertTrue(response.status == 403)

    @unittest_run_loop
    async def test_good_token(self):
        handler = await self.auth_middleware(self.app, self.handler)
        request = make_mocked_request('GET', '/', headers=self.header)
        response = await handler(request)
        self.assertTrue(response.status == 200)
