from aiohttp.test_utils import make_mocked_request, unittest_run_loop

from aiommy.permissions import AuthPermission
from aiommy.unittest import AioTestCase


class AuthPermissionTestCase(AioTestCase):
    @unittest_run_loop
    async def test_request_wo_user(self):
        request = make_mocked_request('GET', '/')
        permission = AuthPermission()
        result = await permission.check_permission(request)
        self.assertTrue(result.status == 401)

    @unittest_run_loop
    async def test_request_none_user(self):
        request = make_mocked_request('GET', '/')
        request.user = None
        permission = AuthPermission()
        result = await permission.check_permission(request)
        self.assertTrue(result.status == 401)

    @unittest_run_loop
    async def test_request_wo_id(self):
        request = make_mocked_request('GET', '/')
        request.user = {'name': 's'}
        permission = AuthPermission()
        result = await permission.check_permission(request)
        self.assertTrue(result.status == 401)

    @unittest_run_loop
    async def test_success_auth_permission(self):
        request = make_mocked_request('GET', '/')
        request.user = {'name': 's', 'id': 1}
        permission = AuthPermission()
        result = await permission.check_permission(request)
        self.assertTrue(result is None)
