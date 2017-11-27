import datetime
import re

import pytz
from aiohttp.test_utils import unittest_run_loop
from aiommy import dateutils
from aiommy.testing import AioTestCase


class DateUtilsTestCase(AioTestCase):
    regex = r'(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})Z'

    def is_equal(self, datetime1, datetime2):
        return all([
            datetime1.year == datetime2.year,
            datetime1.month == datetime2.month,
            datetime1.day == datetime2.day,
            datetime1.hour == datetime2.hour,
            datetime1.minute == datetime2.minute,
        ])

    @unittest_run_loop
    async def test_dateutil_timezone_zero(self):
        timezone = 'UTC'
        dt_with_tz = dateutils.now(timezone)
        dt_native = datetime.datetime.utcnow()
        self.assertTrue(self.is_equal(dt_with_tz, dt_native))

    @unittest_run_loop
    async def test_dateutil_timezone_wo_params(self):
        dt_with_tz = dateutils.now()
        dt_native = datetime.datetime.utcnow()
        self.assertTrue(self.is_equal(dt_with_tz, dt_native))

    @unittest_run_loop
    async def test_dateutil_timezone_plus(self):
        timezone = 'UTC'
        dt_with_tz = dateutils.now(timezone)
        dt_native = datetime.datetime.utcnow() + datetime.timedelta(hours=0)
        self.assertTrue(self.is_equal(dt_with_tz, dt_native))

    @unittest_run_loop
    async def test_dateutil_timezone_minus(self):
        timezone = 'UTC'
        dt_with_tz = dateutils.now(timezone)
        dt_native = datetime.datetime.utcnow() + datetime.timedelta(hours=0)
        self.assertTrue(self.is_equal(dt_with_tz, dt_native))

    @unittest_run_loop
    async def test_dateutil_now_timezone_isoformat(self):
        dt = dateutils.now()
        matched = re.match(self.regex, dateutils.to_iso(dt))
        self.assertTrue(matched is not None)

    @unittest_run_loop
    async def test_dateutil_now_timezone_isoformat_plus(self):
        dt = dateutils.now('Europe/Moscow')
        matched = re.match(self.regex, dateutils.to_iso(dt))
        self.assertTrue(matched is not None)

    @unittest_run_loop
    async def test_dateutil_now_timezone_isoformat_minus(self):
        dt = dateutils.now('Europe/Moscow')
        matched = re.match(self.regex, dateutils.to_iso(dt))
        self.assertTrue(matched is not None)

    @unittest_run_loop
    async def test_dateutil_to_iso(self):
        tz_name = 'UTC'
        self.iso_test(tz_name)

    @unittest_run_loop
    async def test_dateutil_to_iso_plus(self):
        tz_name = 'Europe/Moscow'
        self.iso_test(tz_name)

    @unittest_run_loop
    async def test_dateutil_to_iso_minus(self):
        tz_name = 'America/Argentina/La_Rioja'
        self.iso_test(tz_name)

    def iso_test(self, tz_name):
        utcnow = datetime.datetime.utcnow()
        iso = dateutils.to_iso(utcnow, tz_name)
        matched = re.match(self.regex, iso)
        offseted = utcnow + pytz.timezone(tz_name).utcoffset(utcnow)
        self.assertTrue(offseted.hour == int(matched.group(4)))
