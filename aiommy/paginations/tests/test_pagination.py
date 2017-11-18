from aiohttp.test_utils import unittest_run_loop

from core.unittest import ModelTestCase
from core.paginations.base import BaseCursorPagination
from core.model import Model
from core.db import init_test_db

from app import settings


TEST_DB = init_test_db()


class PaginatorTestCase(ModelTestCase):
    database = TEST_DB
    models = [Model]

    def setUp(self):
        super().setUp()
        for i in range(20):
            Model.create()
        self.paginator = BaseCursorPagination(Model.id, settings.PAGINATE_BY, model=Model)

    @unittest_run_loop
    async def test_init_model(self):
        paginator = BaseCursorPagination(Model.id, model=Model)
        self.assertIs(paginator.model, Model)

    @unittest_run_loop
    async def test_init_model_if_not_passed(self):
        with self.assertRaises(RuntimeError):
            BaseCursorPagination(Model.id)

    @unittest_run_loop
    async def test_pagination_first_page(self):
        queryset = Model.select().order_by(Model.id)
        queryset = self.paginator.first(queryset, None, None)
        result = queryset.execute()
        ids = [i.id for i in result]

        self.assertEqual(len(result), settings.PAGINATE_BY)
        self.assertIn(1, ids)
        self.assertIn(settings.PAGINATE_BY, ids)

    @unittest_run_loop
    async def test_pagination_items_per_page(self):
        items_per_page = 2
        paginator = BaseCursorPagination(Model.id, items_per_page, model=Model)
        paginator.model = Model
        queryset = Model.select().order_by(Model.id)
        queryset = paginator.first(queryset, None, None)
        result = queryset.execute()

        self.assertEqual(len(result), items_per_page)
