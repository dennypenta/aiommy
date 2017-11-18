import peewee
import peewee_async

from app.db import DB


class Model(peewee.Model):
    objects = peewee_async.Manager(DB)

    class Meta:
        database = DB
