from aiohttp.web import HTTPException
from aiommy.json import dumps

JSON_ERROR_KEY = 'error'


class JsonResponse(HTTPException):
    def __init__(self, data=None, status=200, dumps=dumps, **kwargs):
        if not data:
            text = None
            self.empty_body = True
        else:
            text = dumps(data)

        self.status_code = status

        HTTPException.__init__(self, text=text,
                               content_type='application/json',
                               **kwargs)


class JsonErrorResponse(JsonResponse):
    def __init__(self, msg=None, status=400, dumps=dumps, **kwargs):
        data = None
        if msg:
            data = {JSON_ERROR_KEY: msg}

        super().__init__(data=data,
                         status=status,
                         dumps=dumps,
                         **kwargs)
