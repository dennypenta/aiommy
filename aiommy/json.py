import json
import datetime

from core import dateutils
from app import settings


def dumps(data):
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

    indent = None
    if settings.DEV:
        indent = 4
    return json.dumps(data, default=handler, indent=indent)
