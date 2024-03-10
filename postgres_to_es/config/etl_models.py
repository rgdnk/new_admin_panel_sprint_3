# Standard Library
from enum import Enum
from typing import (
    List,
    Optional,
)
from uuid import UUID

# Third Party
from pydantic import BaseModel


class FilmworkType(str, Enum):
    movie = "movie"
    tv_show = "tv_show"


class PersonType(str, Enum):
    actor = "actor"
    director = "director"
    writer = "writer"


class BaseETLModel(BaseModel):
    id: UUID


class PersonFilmWork(BaseETLModel):
    name: str


class Genre(BaseETLModel):
    name: str


class Person(PersonFilmWork):
    role: Optional[List[PersonType]] = None
    film_id: Optional[List[UUID]] = None


class MovieETLSchema(BaseETLModel):
    imdb_rating: Optional[float] = None
    title: str
    description: Optional[str] = None
    genre: Optional[List[str]] = None
    director: Optional[List[str]] = None
    actors_names: Optional[List[str]] = None
    writers_names: Optional[List[str]] = None
    actors: Optional[List[PersonFilmWork]] = None
    writers: Optional[List[PersonFilmWork]] = None
