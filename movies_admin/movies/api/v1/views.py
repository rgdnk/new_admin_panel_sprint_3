# Standard Library
import uuid

# Third Party
from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models import Q
from django.http import JsonResponse
from django.views.generic.detail import BaseDetailView
from django.views.generic.list import BaseListView

# First Party
from movies.models import (
    Filmwork,
    PersonFilmWork,
)


class MoviesApiMixin:
    model = Filmwork
    http_method_names = ["get"]

    def get_queryset(self):
        """Реализация взята отсюда: https://app.pachca.com/chats?thread_id=3049591
        С некоторыми уточнениями.
        """
        return (
            MoviesListApi.model.objects.select_related(
                "genrefilmwork",
                "personfilmwork",
            )
            .values("id", "title", "description", "creation_date", "rating", "type")
            .annotate(
                genres=ArrayAgg("genrefilmwork__genre__name", distinct=True),
                actors=ArrayAgg(
                    "personfilmwork__person__full_name",
                    distinct=True,
                    filter=Q(personfilmwork__role=PersonFilmWork.RoleTypes.ACTOR),
                ),
                directors=ArrayAgg(
                    "personfilmwork__person__full_name",
                    distinct=True,
                    filter=Q(personfilmwork__role=PersonFilmWork.RoleTypes.DIRECTOR),
                ),
                writers=ArrayAgg(
                    "personfilmwork__person__full_name",
                    distinct=True,
                    filter=Q(personfilmwork__role=PersonFilmWork.RoleTypes.WRITER),
                ),
            )
        )

    def render_to_response(self, context, **response_kwargs):
        return JsonResponse(context)


class MoviesListApi(MoviesApiMixin, BaseListView):
    paginate_by = 50

    def get_context_data(self, *, object_list=None, **kwargs):
        queryset = self.get_queryset()
        paginator, page, queryset, is_paginated = self.paginate_queryset(
            queryset,
            self.paginate_by,
        )
        return {
            "count": paginator.count,
            "total_pages": paginator.num_pages,
            "prev": page.previous_page_number() if page.has_previous() else None,
            "next": page.next_page_number() if page.has_next() else None,
            "results": list(queryset),
        }


class MoviesDetailApi(MoviesApiMixin, BaseDetailView):

    def get_context_data(self, **kwargs):
        queryset = self.get_queryset()
        pk = self.get_object(queryset)["id"]
        return queryset.get(id=pk)
