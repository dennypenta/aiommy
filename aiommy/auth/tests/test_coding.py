from aiohttp.test_utils import unittest_run_loop

from core.unittest import AioTestCase
from auth.coding import encode, decode


class CodingTestCase(AioTestCase):
    @unittest_run_loop
    async def test_coding(self):
        payload = {'id': 1}
        token = encode(payload)
        self.assertTrue(isinstance(token, str))

        decoded_payload = decode(token)
        self.assertTrue(payload == decoded_payload)
