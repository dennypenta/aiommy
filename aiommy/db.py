import peewee_asyncext
from app import settings


def init_db():
    return peewee_asyncext.PooledPostgresqlExtDatabase(
        settings.POSTGRES_DB,
        user=settings.POSTGRES_USER,
        password=settings.POSTGRES_PASSWORD,
        host=settings.POSTGRES_HOST,
        port=settings.POSTGRES_PORT,
        threadlocals=True,
        register_hstore=False,
    )


def init_test_db():
    return peewee_asyncext.PooledPostgresqlExtDatabase(
        settings.POSTGRES_TEST_DB,
        user=settings.POSTGRES_TEST_USER,
        password=settings.POSTGRES_TEST_PASSWORD,
        host=settings.POSTGRES_TEST_HOST,
        port=settings.POSTGRES_TEST_PORT,
        register_hstore=False,
    )


def drop_tables():
    DB.set_allow_sync(True)
    DB.drop_tables(MODELS, safe=True, cascade=True)
    print('Tables has been droped succesfully')


def create_tables(safe=False):
    DB.set_allow_sync(True)

    for m in MODELS:
        if not m._meta.db_table:
            raise AttributeError('Attribute `db_table` should be not empty')

    DB.create_tables(MODELS, safe=safe)
    print('Tables has been created succesfully')
