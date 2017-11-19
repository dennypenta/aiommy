import datetime
import json

from aiommy import dateutils


def dumps(data, indent=None):
    def handler(entity):
        if isinstance(entity, datetime.datetime):
            return dateutils.to_iso(entity)
        elif isinstance(entity, bytes):
            return entity.decode('utf-8')
        raise NotImplementedError("""
            You should implement method `dumps(self, data)`
            in your view class
            and override default json handler
        """)

    return json.dumps(data, default=handler, indent=indent)
