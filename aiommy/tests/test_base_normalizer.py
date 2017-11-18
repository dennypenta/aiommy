from aiohttp.test_utils import unittest_run_loop
import peewee

from core.unittest import AioTestCase
from core.model import Model
from core.normalizers import BaseNormalizer


class BaseNormalizerTestCase(AioTestCase):
    def setUp(self):
        super().setUp()

        class TestModel(Model):
            data1 = peewee.IntegerField()
            data2 = peewee.CharField(max_length=20)

        self.model = TestModel
        self.normalizer = BaseNormalizer()
        self.instance = self.model(id=1, data1=1, data2='2')
        self.expected = {'id': 1, 'data1': 1, 'data2': '2'}

    @unittest_run_loop
    async def test_normalize_object(self):
        normalized = self.normalizer.normalize_object(self.instance)
        self.assertEqual(self.expected, normalized)

    @unittest_run_loop
    async def test_normalize(self):
        normalized = self.normalizer.normalize([self.instance, self.instance])
        self.assertEqual(normalized, [self.expected, self.expected])

    @unittest_run_loop
    async def test_fields_set(self):
        class FieldNormalizer(BaseNormalizer):
            fields = ('data1', )

        normalizer = FieldNormalizer()
        normalized = normalizer.normalize_object(self.instance)
        self.assertNotIn('data2', normalized)
