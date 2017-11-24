import unittest

from peewee import Model

from aiommy.db import Manager, inject_db
from tests.fixtures import TEST_DB


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


class ManagerTestCase(unittest.TestCase):
    def test_manager_init(self):
        Manager._instance = None
        self.assertIsNone(Manager._instance)

        instance1 = Manager.init(TEST_DB)
        instance2 = Manager.init(TEST_DB)

        self.assertEqual(instance1, instance2)
        self.assertEqual(instance1, Manager._instance)

    def test_integrate_manager_and_model(self):
        class TestModel(Model):
            objects = Manager.init(TEST_DB)

        manager = Manager.init(TEST_DB)

        self.assertEqual(manager, TestModel.objects)

    def test_raise_warning_if_has_been_inited_one_more(self):
        Manager.init(TEST_DB)

        with self.assertWarns(Warning):
            Manager.init(TEST_DB)
