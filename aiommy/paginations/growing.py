from aiommy.paginations.base import BaseCursorPagination


class GrowingPagination(BaseCursorPagination):
    def first(self, queryset, through, last_id):
        """
        :param queryset: peewee queryset
        :param through: params for save interface for all paginate methods
        :param last_id: id of last element for exclude duplicating
        :return: paginated queryset
        """
        return queryset.order_by(self.cursor, self.model.id).paginate(1, self.items_per_page)

    def next(self, queryset, through, last_id=None):
        where_exp = (self.cursor > through) | ((self.cursor == through) & (self.model.id > last_id))

        return queryset.where(where_exp)\
            .order_by(self.cursor, self.model.id)\
            .paginate(1, self.items_per_page)

    def previous(self, queryset, through, last_id=None):
        where_exp = (self.cursor < through) | ((self.cursor == through) & (self.model.id < last_id))

        return queryset.where(where_exp)\
            .order_by(-self.cursor, self.model.id)
