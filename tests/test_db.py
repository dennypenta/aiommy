from aiommy.db import inject_db
from peewee import Model

from tests.fixtures import TEST_DB

import unittest


class InjectDbTestCase(unittest.TestCase):
    def test_db_injected(self):
        table_name = 'table_name'

        @inject_db(TEST_DB)
        class ModelWithInjectedDb(Model):
            class Meta:
                table_name = 'table_name'

        self.assertEqual(ModelWithInjectedDb.__name__, 'ModelWithInjectedDb')
        self.assertEqual(ModelWithInjectedDb._meta.table_name, table_name)
        self.assertEqual(ModelWithInjectedDb._meta.database, TEST_DB)
        self.assertEqual(ModelWithInjectedDb.objects.database, TEST_DB)
