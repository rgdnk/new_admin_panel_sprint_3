# Standard Library
import os
import sqlite3
from pathlib import Path

# Third Party
import psycopg2
from dotenv import load_dotenv
from postgres_dataclasses import (
    FilmWork,
    Genre,
    GenreFilmWork,
    Person,
    PersonFilmWork,
)
from postgres_saver import PGSaver
from psycopg2.extensions import connection as _connection
from psycopg2.extras import NamedTupleCursor
from sqlite_extractor import SQLiteExtractor


dotenv_path = Path(__file__).resolve().parent.parent / "db.env"
load_dotenv(dotenv_path)


TABLE_DATACLASS_DICT = {
    "film_work": FilmWork,
    "genre": Genre,
    "person": Person,
    "genre_film_work": GenreFilmWork,
    "person_film_work": PersonFilmWork,
}

PAGE_SIZE = int(os.environ.get("PAGE_SIZE"))


def load_one_table(connection: sqlite3.Connection, pg_conn: _connection, table_name):
    postgres_saver = PGSaver(pg_conn, schema="content", page_size=PAGE_SIZE)
    sqlite_extractor = SQLiteExtractor(connection, page_size=PAGE_SIZE)
    columns = ", ".join(TABLE_DATACLASS_DICT[table_name].__dataclass_fields__.keys())
    for data in sqlite_extractor.get_sqlite_data(
        table_name=table_name,
        columns=columns,
        page_size=PAGE_SIZE,
    ):
        dataclass_object = [
            TABLE_DATACLASS_DICT[table_name](*data_object) for data_object in data
        ]
        postgres_saver.save_all_data(table_name, dataclass_object, column_names=columns)


def load_from_sqlite(connection: sqlite3.Connection, pg_conn: _connection):
    for table in TABLE_DATACLASS_DICT.keys():
        try:
            load_one_table(connection, pg_conn, table)
        except psycopg2.errors.ForeignKeyViolation as e:
            raise e


if __name__ == "__main__":
    dsl = {
        "dbname": os.environ.get("POSTGRES_DB"),
        "user": os.environ.get("POSTGRES_USER"),
        "password": os.environ.get("POSTGRES_PASSWORD"),
        "host": os.environ.get("POSTGRES_LOCAL_HOST", "127.0.0.1"),
        "port": os.environ.get("POSTGRES_PORT", 5432),
    }
    # Теперь с контекстным менеджером
    with SQLiteExtractor(
        sqlite3.connect(os.environ.get("SQLITE_PATH")),
        page_size=PAGE_SIZE,
    ).conn_context() as sqlite_conn, psycopg2.connect(
        **dsl,
        cursor_factory=NamedTupleCursor,
    ) as pg_conn:
        load_from_sqlite(sqlite_conn, pg_conn)
