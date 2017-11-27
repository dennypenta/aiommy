import unittest
from copy import copy

from aiommy.db import Manager, inject_db
from peewee import Model
from tests.fixtures import TEST_DB


class InjectDbTestCase(unittest.TestCase):
    def test_db_injected(self):
        db_table = 'table_name'

        @inject_db(TEST_DB)
        class ModelWithInjectedDb(Model):
            class Meta:
                db_table = 'table_name'

        self.assertEqual(ModelWithInjectedDb.__name__, 'ModelWithInjectedDb')
        self.assertEqual(ModelWithInjectedDb._meta.db_table, db_table)
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
            Manager.init(copy(TEST_DB))

    def test_many_model_each_other_inject(self):
        @inject_db(TEST_DB)
        class Model1(Model):
            pass

        @inject_db(TEST_DB)
        class Model2(Model):
            pass

        self.assertEqual(Model1.objects, Model2.objects)
