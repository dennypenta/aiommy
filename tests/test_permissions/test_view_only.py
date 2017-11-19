from aiohttp.test_utils import make_mocked_request, unittest_run_loop

from aiommy.permissions import ViewOnly
from aiommy.unittest import AioTestCase


class AuthPermissionTestCase(AioTestCase):
    @unittest_run_loop
    async def test_fail(self):
        request = make_mocked_request('POST', '/')
        permission = ViewOnly()
        result = await permission.check_permission(request)
        self.assertTrue(result.status == 405)

    @unittest_run_loop
    async def test_success_get(self):
        request = make_mocked_request('GET', '/')
        permission = ViewOnly()
        result = await permission.check_permission(request)
        self.assertTrue(result is None)
