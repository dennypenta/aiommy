from aiohttp.test_utils import unittest_run_loop

from aiommy.paginations.base import BaseCursorPagination
from aiommy.unittest import ModelTestCase
from tests.fixtures import TEST_DB, TestModel

PAGINATE_BY = 10


class PaginatorTestCase(ModelTestCase):
    database = TEST_DB
    models = [TestModel]

    def setUp(self):
        super().setUp()
        for i in range(20):
            TestModel.create()
        self.paginator = BaseCursorPagination(TestModel.id, PAGINATE_BY, model=TestModel)

    @unittest_run_loop
    async def test_init_model(self):
        paginator = BaseCursorPagination(TestModel.id, PAGINATE_BY, model=TestModel)
        self.assertIs(paginator.model, TestModel)

    @unittest_run_loop
    async def test_pagination_first_page(self):
        queryset = TestModel.select().order_by(TestModel.id)
        queryset = self.paginator.first(queryset, None, None)
        result = queryset.execute()
        ids = [i.id for i in result]

        self.assertEqual(len(result), PAGINATE_BY)
        self.assertIn(1, ids)
        self.assertIn(PAGINATE_BY, ids)

    @unittest_run_loop
    async def test_pagination_items_per_page(self):
        items_per_page = 2
        paginator = BaseCursorPagination(TestModel.id, items_per_page, model=TestModel)
        paginator.model = TestModel
        queryset = TestModel.select().order_by(TestModel.id)
        queryset = paginator.first(queryset, None, None)
        result = queryset.execute()

        self.assertEqual(len(result), items_per_page)
