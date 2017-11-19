import peewee
import peewee_async

from aiommy.unittest import ModelTestCase

TEST_DB = peewee_async.PooledPostgresqlDatabase(
    'test_db',
    user='denny',
)


class TestModel(peewee.Model):
    objects = peewee_async.Manager(TEST_DB)

    class Meta:
        table_name = 'test_table'
        database = TEST_DB


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
