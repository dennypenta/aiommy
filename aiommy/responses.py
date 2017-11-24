from aiommy.json import dumps

from aiohttp.web import HTTPException


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
