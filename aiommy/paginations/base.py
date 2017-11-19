class BasePagination(object):
    """
    Class that make queryset paginated
    """
    model = None

    def __init__(self, cursor, items_per_page, model):
        """
        :param cursor: field that would be direction for pagination
        :param items_per_page: items per each page
        :param model: model class for binding  paginator
        """
        self._cursor = cursor
        self._items_per_page = items_per_page
        self.model = model

    @property
    def items_per_page(self):
        return self._items_per_page

    @property
    def cursor(self):
        return self._cursor

    def first(self, queryset, through, last_id):
        """
        :param queryset: peewee queryset that should be paginated
        :param through: params for save interface for all paginte methods
        :return: paginated queryset
        :param last_id: id of last element for exclude duplicating
        """
        return queryset

    def next(self, queryset, through, last_id):
        """
        :param queryset: peewee queryset that should be paginated
        :param through: cursor params that point to helpful value for pagination
        :return: paginated queryset
        :param last_id: id of last element for exclude duplicating
        """
        return queryset

    def previous(self, queryset, through, last_id):
        """
        :param queryset: peewee queryset that should be paginated
        :param through: cursor params that point to helpful value for pagination
        :return: paginated queryset
        :param last_id: id of last element for exclude duplicating
        """
        return queryset


class BaseCursorPagination(BasePagination):
    def first(self, queryset, through, last_id):
        """
        :param queryset: peewee queryset
        :param through: params for save interface for all paginate methods
        :param last_id: id of last element for exclude duplicating
        :return: paginated queryset
        """
        return queryset.order_by(self.cursor, self.model.id).paginate(1, self.items_per_page)
