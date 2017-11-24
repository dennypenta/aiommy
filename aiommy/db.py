import warnings

import peewee
import peewee_async


class Manager(object):
    _instance = None
    _manager = None

    @classmethod
    def init(cls, db):
        if not isinstance(db, peewee.Database):
            raise TypeError('db should be instance of `peewee.Database`')

        if cls._instance:
            if cls._instance.database is not db:
                warnings.warn('Now we are not checking that injected database '
                              'is the same as database were injected before',
                              category=Warning)
            return cls._instance

        cls._instance = cls(db)
        return cls._instance

    def __init__(self, db):
        self._manager = peewee_async.Manager(db)

    def __get__(self, instance, owner):
        return self._manager


def inject_db(db):
    def class_decorator(cls):
        class DatabaseInjectedClass(cls):
            objects = Manager.init(db)

            class Meta:
                db_table = cls._meta.db_table
                database = db

        DatabaseInjectedClass. __name__ = cls.__name__
        DatabaseInjectedClass.__doc__ = cls.__doc__

        return DatabaseInjectedClass

    return class_decorator
