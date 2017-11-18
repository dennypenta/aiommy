from aiohttp import web
from cerberus import Validator

from core.json import dumps
from core.normalizers import BaseNormalizer


class BaseView(web.View):
    permissions = ()


class JsonifyResponseView(BaseView):
    def json_response(self, data, status=200):
        return web.json_response(data, dumps=dumps, status=status)


METHODS_WITH_BODY = ('POST', 'PATCH', 'PUT')


class RequestValidator(object):
    query = Validator({}, allow_unknown=True)
    headers = Validator({}, allow_unknown=True)
    params = Validator({}, allow_unknown=True)
    body = Validator({}, allow_unknown=True)

    def __init__(self, request, **kwargs):
        self.request = request
        self.query = kwargs.get('query_validator', self.query)
        self.headers = kwargs.get('header_validator', self.headers)
        self.params = kwargs.get('params_validator', self.params)
        self.body = kwargs.get('body_validator', self.body)

    async def validate(self):
        for handler in self.handlers:
            err = await handler()
            if err:
                return err

    async def validate_request(self):
        return await self.validate()

    @property
    def handlers(self):
        return (
            self.validated_query,
            self.validate_params,
            self.validated_headers,
            self.validate_body,
        )

    async def validated_query(self):
        if not self.query.validate(dict(self.request.query)):
            return self.query.errors

    async def validated_headers(self):
        if not self.headers.validate(dict(self.request.headers)):
            return self.headers.errors

    async def validate_params(self):
        if not self.params.validate(dict(self.request.match_info)):
            return self.params.errors

    async def validate_body(self):
        if self.request.method not in METHODS_WITH_BODY:
            return

        if not self.body.validate(await self.request.json()):
            return self.body.errors


class ListView(JsonifyResponseView):
    model = None
    normalizer = BaseNormalizer()
    pagination = None
    validator = RequestValidator

    def get_queryset(self):
        if not self.model:
            raise AttributeError('You should set "model" as class-view parameter')

        return self.model.select()

    def paginate(self, queryset):
        if not self.pagination:
            return queryset

        rule = self.validator.query.document.get('paginate_to', 'first')
        through = self.validator.query.document.get('paginate_through')
        last_id = self.validator.query.document.get('last_id', None)
        return getattr(self.pagination, rule)(queryset, through, last_id)

    async def normalize(self, queryset):
        executed = await self.model.objects.execute(queryset)
        return self.normalizer.normalize(executed)

    async def validate_request(self):
        validator_classes = self.init_validator_classes()
        validator = self.validator(self.request, **validator_classes)
        return await validator.validate_request()

    def init_validator_classes(self):
        return {}

    async def get(self):
        err = await self.validate_request()
        if err:
            return self.json_response(err, status=400)

        queryset = self.get_queryset()
        paginated = self.paginate(queryset)
        normalized = await self.normalize(paginated)
        return self.json_response(normalized)
