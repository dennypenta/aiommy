import datetime

import pytz

FORMAT = '%Y-%m-%dT%H:%M:%SZ'


def now(timezone='UTC'):
    return pytz.timezone(timezone).localize(datetime.datetime.utcnow())


def to_iso(dt, tz_name='UTC'):
    result = dt + pytz.timezone(tz_name).utcoffset(dt)
    return result.strftime(FORMAT)


def from_iso_to_datetime(dt, tz_name='UTC'):
    return datetime.datetime.strptime(dt, FORMAT)
