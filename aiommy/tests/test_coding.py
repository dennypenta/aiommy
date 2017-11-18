from aiohttp.test_utils import unittest_run_loop


from core.unittest import AioTestCase
from core.middlewares import encode, decode


class CodingTestCase(AioTestCase):
    @unittest_run_loop
    async def coding_test(self):
        payload = {'id': 1}
        token = encode(payload)
        self.assertTrue(isinstance(token, str))

        decoded_payload = decode(token)
        self.assertTrue(payload == decoded_payload)
