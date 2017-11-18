from playhouse import shortcuts


class CoreNormalizer(object):
    fields = None

    def _model_to_dict(self, model_object):
        raise NotImplemented

    def normalize(self, queryset):
        return [self.normalize_object(i) for i in queryset]

    def normalize_object(self, model_object):
        if self.fields:
            return {field: getattr(model_object, field) for field in self.fields}
        return shortcuts.model_to_dict(model_object)


class BaseNormalizer(CoreNormalizer):
    def _model_to_dict(self, model_object):
        return shortcuts.model_to_dict(model_object)
