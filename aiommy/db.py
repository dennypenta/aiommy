import peewee_async


def inject_db(db):
    def class_decorator(cls):
        class DatabaseInjectedClass(cls):
            objects = peewee_async.Manager(db)

            class Meta:
                table_name = cls._meta.table_name
                database = db

        DatabaseInjectedClass. __name__ = cls.__name__
        DatabaseInjectedClass.__doc__ = cls.__doc__

        return DatabaseInjectedClass

    return class_decorator
