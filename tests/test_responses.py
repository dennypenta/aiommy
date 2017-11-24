from aiohttp.web import HTTPException

from aiommy.responses import JsonResponse
from aiommy.unittest import AioTestCase


class JsonResponseTestCase(AioTestCase):
    response_data = [dict(expect='{"data": 1}',
                          data={'data': 1}),
                     dict(expect='[{"data": 1}]',
                          data=[{'data': 1}]),
    ]

    def test_simple_response(self):
        response = JsonResponse()

        self.assertEqual(response.status, 200)

    def test_response_with_other_status(self):
        status = 400
        response = JsonResponse(status=status)

        self.assertEqual(response.status, status)

    def test_response_raise(self):
        with self.assertRaises(JsonResponse) and self.assertRaises(HTTPException):
            raise JsonResponse()

    def test_response_raise_other_status(self):
        status = 400

        try:
            raise JsonResponse(status=status)
        except HTTPException as err:
            self.assertEqual(err.status, status)

    def test_wo_data(self):
        response = JsonResponse()

        self.assertIsNone(response.text)

    def test_response_data(self):
        for data in self.response_data:
            response = JsonResponse(data['data'])
            self.assertEqual(data['expect'], response.text)

    def test_content_type(self):
        response = JsonResponse()

        self.assertEqual(response.content_type, 'application/json')

    def test_raise_wo_data(self):
        try:
            raise JsonResponse()
        except HTTPException as err:
            self.assertIsNone(err.text)

    def test_raise_with_data(self):
        for data in self.response_data:
            try:
                raise JsonResponse(data['data'])
            except HTTPException as err:
                self.assertEqual(err.text, data['expect'])
