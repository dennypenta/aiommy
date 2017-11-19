import datetime

from aiohttp.test_utils import unittest_run_loop

from aiommy.json import dumps
from aiommy.unittest import AioTestCase


class JsonTestCase(AioTestCase):
    @unittest_run_loop
    async def test_datetime_json(self):
        data = {'date': datetime.datetime.now()}
        result = dumps(data)
        self.assertTrue(isinstance(result, str))

    @unittest_run_loop
    async def test_date_json(self):
        data = {'date': datetime.datetime.now()}
        result = dumps(data)
        self.assertTrue(isinstance(result, str))

    @unittest_run_loop
    async def test_bytes_json(self):
        data = {'bytes': bytes('bytesting'.encode('utf-8'))}
        result = dumps(data)
        self.assertTrue(isinstance(result, str))
        self.assertTrue(not result.startswith("b'"))
