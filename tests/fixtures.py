from functools import wraps

import peewee
import peewee_async
from aiommy.testing import ModelTestCase
from playhouse.shortcuts import RetryOperationalError

DB_NAME = 'test_db'
DB_OPTIONS = {
    'user': 'denny'
}

TEST_DB = peewee_async.PooledPostgresqlDatabase(
    DB_NAME,
    **DB_OPTIONS,
)


class AutoReconnectionDatabase(RetryOperationalError, peewee_async.PooledPostgresqlDatabase):
    pass


class TestModel(peewee.Model):
    objects = peewee_async.Manager

    class Meta:
        database = TEST_DB
        table_name = 'test_table'


class ExtendedTestModel(TestModel):
    data1 = peewee.IntegerField()
    data2 = peewee.CharField(max_length=20)


class TestingPaginationModel(peewee.Model):
    date = peewee.DateTimeField()

    class Meta:
        db_table = 'test_table'


class PaginationTestCase(ModelTestCase):
    def setUp(self):
        TestingPaginationModel._meta.database = self.database
        TestingPaginationModel.objects = peewee_async.Manager(self.database)
        self.models.append(TestingPaginationModel)
        super().setUp()
