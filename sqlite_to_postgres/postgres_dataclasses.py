# Standard Library
import uuid
from dataclasses import (
    dataclass,
    field,
)
from datetime import (
    datetime,
    timezone,
)
from typing import Optional


@dataclass
class FilmWork:
    title: str
    description: Optional[str]
    creation_date: Optional[datetime]
    file_path: str
    rating: Optional[float]
    type: str
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    created_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))
    updated_at: Optional[datetime] = field(
        default_factory=lambda: datetime.now(tz=timezone.utc),
    )


@dataclass
class Person:
    full_name: str
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    created_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))
    updated_at: Optional[datetime] = field(
        default_factory=lambda: datetime.now(tz=timezone.utc),
    )


@dataclass
class Genre:
    name: str
    description: Optional[str]
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    created_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))
    updated_at: Optional[datetime] = field(
        default_factory=lambda: datetime.now(tz=timezone.utc),
    )


@dataclass
class PersonFilmWork:
    role: str
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    film_work_id: uuid.UUID = field(default_factory=uuid.uuid4)
    person_id: uuid.UUID = field(default_factory=uuid.uuid4)
    created_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))


@dataclass
class GenreFilmWork:
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    genre_id: uuid.UUID = field(default_factory=uuid.uuid4)
    film_work_id: uuid.UUID = field(default_factory=uuid.uuid4)
    created_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))
