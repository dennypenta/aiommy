from aiohttp.test_utils import unittest_run_loop, make_mocked_request

from core.permissions.base import BasePermission
from core.unittest import AioTestCase


class BasePermissionTestCase(AioTestCase):
    @unittest_run_loop
    async def test_check_permission(self):
        request = make_mocked_request('GET', '/')
        permission = BasePermission()
        result = await permission.check_permission(request)
        self.assertTrue(result is None)

    @unittest_run_loop
    async def test_get_response(self):
        permission = BasePermission()
        result = await permission.get_response()
        self.assertTrue(result.status == 403)
