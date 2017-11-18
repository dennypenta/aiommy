from aiohttp.test_utils import unittest_run_loop

from core.unittest import ModelTestCase, TestingPaginationModel
from core.db import init_test_db
from core.paginations.falling import FallingPagination
from app import settings

import datetime


class FallingPaginationTestCase(ModelTestCase):
    database = init_test_db()
    models = [TestingPaginationModel]

    def create_fixtures(self):
        self.objects_number = 50
        self.recomend_delta_for_testing = 25
        self.now = datetime.datetime.utcnow()
        objects = (dict(
            date=self.now - datetime.timedelta(days=i),
        ) for i in range(self.objects_number))
        TestingPaginationModel.insert_many(objects).execute()

        self.paginator = FallingPagination(TestingPaginationModel.date,
                                           model=TestingPaginationModel)

    @unittest_run_loop
    async def test_next_page(self):
        queryset = TestingPaginationModel.select()
        through = self.now - datetime.timedelta(days=self.recomend_delta_for_testing)
        paginated = self.paginator.next(queryset, through, self.recomend_delta_for_testing)

        self.assertEqual(len(paginated), settings.PAGINATE_BY)
        for obj in paginated:
            self.assertLessEqual(obj.date, through)

    @unittest_run_loop
    async def test_previous_page(self):
        last_id = 30
        queryset = TestingPaginationModel.select()
        through = self.now - datetime.timedelta(days=30)
        paginated = self.paginator.previous(queryset, through, last_id)

        self.assertGreater(len(paginated), settings.PAGINATE_BY)
        for obj in paginated:
            self.assertGreaterEqual(obj.date, through)

    @unittest_run_loop
    async def test_first_page(self):
        queryset = TestingPaginationModel.select()
        paginated = self.paginator.first(queryset, None, None)

        self.assertEqual(len(paginated), settings.PAGINATE_BY)

    @unittest_run_loop
    async def test_items_per_page(self):
        queryset = TestingPaginationModel.select()
        paginated = self.paginator.first(queryset, None, None)

        self.assertEqual(len(paginated), settings.PAGINATE_BY)


class FallingLastIdTestCase(ModelTestCase):
    database = init_test_db()
    models = [TestingPaginationModel]

    def create_fixtures(self):
        self.duplicated_date = datetime.datetime.utcnow() + datetime.timedelta(days=3)
        self.objects = [
            dict(id=1, date=self.duplicated_date),
            dict(id=2, date=self.duplicated_date),
            dict(id=3, date=datetime.datetime.utcnow() + datetime.timedelta(days=1)),
            dict(id=4, date=datetime.datetime.utcnow() + datetime.timedelta(days=2)),
        ]
        TestingPaginationModel.insert_many(self.objects).execute()
        self.paginator = FallingPagination(TestingPaginationModel.date,
                                           model=TestingPaginationModel)

    @unittest_run_loop
    async def test_last_id_pagination(self):
        last_id = 1
        queryset = TestingPaginationModel.select()
        paginated = self.paginator.next(queryset, self.duplicated_date, last_id)

        for obj in paginated:
            try:
                self.assertLess(obj.date, self.duplicated_date)
            except AssertionError:
                self.assertGreater(obj.id, last_id)
