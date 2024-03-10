# Standard Library
import logging
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
from pydantic import Field
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)
from sqlite_extractor import SQLiteExtractor


class PostgresConnectParameters(BaseSettings):
    dbname: str = Field(alias="POSTGRES_DB")
    user: str = Field(alias="POSTGRES_USER")
    password: str = Field(alias="POSTGRES_PASSWORD")
    host: str = Field(alias="POSTGRES_HOST")
    port: int = Field(alias="POSTGRES_PORT")

    model_config = SettingsConfigDict(
        env_file="db.env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


class ProcessParameters(BaseSettings):
    page_size: int = Field(alias="PAGE_SIZE")
    sqlite_path: str = Field(alias="SQLITE_PATH")

    model_config = SettingsConfigDict(
        env_file="db.env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


process_parameters = ProcessParameters()

logger = logging.getLogger(__name__)


TABLE_DATACLASS_DICT = {
    "film_work": FilmWork,
    "genre": Genre,
    "person": Person,
    "genre_film_work": GenreFilmWork,
    "person_film_work": PersonFilmWork,
}


def load_one_table(connection: sqlite3.Connection, pg_conn: _connection, table_name):
    postgres_saver = PGSaver(
        pg_conn,
        schema="content",
        page_size=process_parameters.page_size,
    )
    sqlite_extractor = SQLiteExtractor(
        connection,
        page_size=process_parameters.page_size,
    )
    columns = ", ".join(TABLE_DATACLASS_DICT[table_name].__dataclass_fields__.keys())
    for data in sqlite_extractor.get_sqlite_data(
        table_name=table_name,
        columns=columns,
        page_size=process_parameters.page_size,
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
    logger.info(msg="Transfer process started")
    dsn = PostgresConnectParameters
    # Теперь с контекстным менеджером
    with SQLiteExtractor(
        sqlite3.connect(process_parameters.sqlite_path),
        page_size=process_parameters.page_size,
    ).conn_context() as sqlite_conn, psycopg2.connect(
        **dsn().model_dump(),
        cursor_factory=NamedTupleCursor,
    ) as pg_conn:
        load_from_sqlite(sqlite_conn, pg_conn)
        logger.info(msg="Transfer progress ended")
