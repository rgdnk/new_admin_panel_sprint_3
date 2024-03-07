# Third Party
from django.contrib import admin

# First Party
from movies.models import (
    Filmwork,
    Genre,
    GenreFilmWork,
    Person,
    PersonFilmWork,
)


class GenreFilmworkInline(admin.TabularInline):
    model = GenreFilmWork


class PersonFilmworkInline(admin.TabularInline):
    model = PersonFilmWork


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ("name", "description")
    search_fields = ("name", "description", "id")


@admin.register(Filmwork)
class FilmworkAdmin(admin.ModelAdmin):
    inlines = (GenreFilmworkInline, PersonFilmworkInline)
    list_display = (
        "title",
        "type",
        "creation_date",
        "rating",
        "created_at",
        "updated_at",
    )
    list_filter = ("type",)
    search_fields = (
        "title",
        "description",
        "id",
    )


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ("full_name",)
    search_fields = (
        "full_name",
        "id",
    )
