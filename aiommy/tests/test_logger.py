from aiohttp.test_utils import unittest_run_loop

from core.unittest import AioTestCase
from core.logger import Logger
from app import settings

import logging
import os


class LoggerTestCase(AioTestCase):
    def setUp(self):
        super().setUp()
        self.name = 'name'
        self.path = settings.BASE_DIR + 'test.log'
        self.level = logging.INFO

    def tearDown(self):
        super().tearDown()
        os.remove(self.path)

    @unittest_run_loop
    async def test_init_log(self):
        logger = Logger(self.name, self.path, self.level)

        self.assertEqual(logger.logger.name, self.name)
        self.assertEqual(logger.logger.level, self.level)

        logger.logger.error('test log')

        self.assertTrue(os.path.exists(self.path))

    @unittest_run_loop
    async def test_log_error(self):
        logger = Logger(self.name, self.path, self.level)
        with self.assertLogs(self.name, logging.ERROR):
            logger.error('test error log')

        with open(self.path) as f:
            self.assertIsNotNone(f.read())
