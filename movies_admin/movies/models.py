# Standard Library
import uuid

# Third Party
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


"""Использую собственный валидатор рейтинга,
так как встроенный MinValueValidator не дает оставить поле пустым.
Пустое поле рейтинга кажется логичным для еще не вышедших фильмов
или фильмов без оценок."""


def validate_negative_rating(value):
    if value < 0:
        raise ValidationError(
            _("%(value)s is negative, please leave blank or fill with positive number"),
            params={"value": value},
        )


class TimeStampedMixin(models.Model):
    class Meta:
        abstract = True

    created_at = models.DateTimeField(_("Created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated at"), auto_now=True)


class UUIDMixin(models.Model):
    class Meta:
        abstract = True

    id = models.UUIDField(
        name="id",
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )


"""
В приложенной БД db.sqlite текстовые поля содержат NULL, и при попытке оставить
только blank=True я получаю NotNullViolation.
Прочитал, что в Django параметр null относится к состоянию поля в базе данных,
а blank - к валидации вводимого в форму значения.
Хотя их совмещение в текстовых полях не рекомендуется, одного blank=True
может быть недостаточно, так как в этом случае Django
при попытке сохранить объект с пустым значением выдаст ошибку.
Предлагаю оставить конструкцию blank=True, null=True.
"""


class Genre(UUIDMixin, TimeStampedMixin):
    class Meta:
        db_table = 'content"."genre'
        verbose_name = _("Genre")
        verbose_name_plural = _("Genres")

    name = models.CharField(_("Name"), max_length=255)
    description = models.TextField(_("Description"), blank=True, null=True)

    def __str__(self):
        return self.name


class Person(UUIDMixin, TimeStampedMixin):
    class Meta:
        db_table = 'content"."person'
        verbose_name = _("Actor")
        verbose_name_plural = _("Actors")

    full_name = models.CharField(_("full name"), max_length=255)

    def __str__(self):
        return self.full_name


class Filmwork(UUIDMixin, TimeStampedMixin):
    class Meta:
        db_table = 'content"."film_work'
        indexes = [
            models.Index(fields=["creation_date"], name="film_work_creation_date_idx"),
        ]
        verbose_name = _("Film")
        verbose_name_plural = _("Films")

    class FilmworkTypes(models.TextChoices):
        MOVIE = "movie"
        TV_SHOW = "tv show"

    title = models.CharField(_("Title"), max_length=255)
    description = models.TextField(_("Description"), blank=True, null=True)
    creation_date = models.DateField(
        _("Creation date"),
        blank=True,
        null=True,
    )
    file_path = models.CharField(_("file_path"), max_length=512, blank=True, null=True)
    rating = models.FloatField(
        _("Rating"),
        blank=True,
        null=True,
        validators=[validate_negative_rating, MaxValueValidator(100)],
    )
    type = models.TextField(_("Type"), choices=FilmworkTypes.choices)
    genre_id = models.ManyToManyField(Genre, through="GenreFilmWork")
    person_id = models.ManyToManyField(Person, through="PersonFilmWork")

    def __str__(self):
        return self.title


class GenreFilmWork(UUIDMixin):
    class Meta:
        db_table = 'content"."genre_film_work'
        indexes = [
            models.Index(
                name="film_work_genre_idx",
                fields=["film_work_id", "genre_id"],
            ),
        ]

    created_at = models.DateTimeField(auto_now_add=True)
    film_work = models.ForeignKey("Filmwork", on_delete=models.DO_NOTHING)
    genre = models.ForeignKey("Genre", on_delete=models.DO_NOTHING)


class PersonFilmWork(UUIDMixin):
    class Meta:
        db_table = 'content"."person_film_work'
        constraints = [
            models.UniqueConstraint(
                name="film_work_person_role_ctr",
                fields=["film_work_id", "person_id", "role"],
            ),
        ]

    class RoleTypes(models.TextChoices):
        ACTOR = "actor"
        DIRECTOR = "director"
        WRITER = "writer"

    role = models.TextField(_("Role"), choices=RoleTypes.choices)
    created_at = models.DateTimeField(auto_now_add=True)
    film_work = models.ForeignKey("Filmwork", on_delete=models.DO_NOTHING)
    person = models.ForeignKey("Person", on_delete=models.DO_NOTHING)
