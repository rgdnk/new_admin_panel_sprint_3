# Standard Library
import os
import sqlite3
from datetime import (
    datetime,
    timezone,
)
from pathlib import Path

# Third Party
import psycopg2
from dateutil import parser
from dotenv import load_dotenv


dotenv_path = Path(__file__).resolve().parent.parent.parent / "movies_admin/.env"
load_dotenv(dotenv_path)

dsl = {
    "dbname": os.environ.get("DB_NAME"),
    "user": os.environ.get("DB_USER"),
    "password": os.environ.get("DB_PASSWORD"),
    "host": os.environ.get("DB_HOST", "127.0.0.1"),
    "port": os.environ.get("DB_PORT", 5432),
}


def convert_datetime_iso(val):
    date_object = parser.parse(val)
    return date_object.replace(tzinfo=timezone.utc)


def convert_date(val):
    return datetime.date.fromisoformat(val.decode()).replace(tzinfo=timezone.utc)


pg_schema = "content"
tables_to_check = [
    "film_work",
    "genre",
    "person",
    "genre_film_work",
    "person_film_work",
]


def get_rows_count_assertion(
    table_name,
    sqlite_conn: sqlite3.connect,
    pg_conn: psycopg2.connect,
    schema_name=None,
):
    sqlite_cursor = sqlite_conn.cursor()
    count_query = f"select count(*) from {table_name};"
    sqlite_cursor.execute(count_query)
    sqlite_rows_count = sqlite_cursor.fetchone()[0]

    pg_cursor = pg_conn.cursor()
    if schema_name:
        count_query = f"select count(*) from {schema_name}.{table_name};"
    pg_cursor.execute(count_query)
    pg_rows_count = pg_cursor.fetchone()[0]

    assert sqlite_rows_count == pg_rows_count


def get_table_data_equality_assertion(
    table_name,
    sqlite_conn: sqlite3.connect,
    pg_conn: psycopg2.connect,
    schema_name=None,
):
    sqlite_cursor = sqlite_conn.cursor()
    sqlite_cursor.execute(f"PRAGMA table_info({table_name})")
    sqlite_columns = [column[1] for column in sqlite_cursor.fetchall()]

    pg_cursor = pg_conn.cursor()
    if schema_name:
        pg_cursor.execute(
            f"select column_name from information_schema.columns "
            f"where table_name = '{table_name}'"
            f"and table_schema = '{schema_name}'",
        )
    pg_columns = [column[0] for column in pg_cursor.fetchall()]

    assert sorted(sqlite_columns) == sorted(
        pg_columns,
    ), f"Houston we have a columns assertion mismatch problem in {table_name}"

    sqlite3.register_converter("timestamp", convert_datetime_iso)
    sqlite3.register_converter("date", convert_date)
    equal_query = (
        f"select {','.join(sorted(sqlite_columns))} from {table_name} order by id;"
    )
    sqlite_cursor.execute(equal_query)
    sqlite_table_column_data = sqlite_cursor.fetchall()
    if schema_name:
        equal_query = f"select {','.join(sorted(pg_columns))} from {schema_name}.{table_name} order by id;"
    pg_cursor.execute(equal_query)
    pg_table_column_data = pg_cursor.fetchall()
    for sqlite_row, pg_row in zip(sqlite_table_column_data, pg_table_column_data):
        assert (
            sqlite_row == pg_row
        ), f"Assertion fails on table {table_name}, sqlite row: {sqlite_row},\npg row: {pg_row}"


if __name__ == "__main__":
    with sqlite3.connect(
        os.environ.get("SQLITE_PATH"),
        detect_types=1,
    ) as sqlite_conn, psycopg2.connect(
        **dsl,
    ) as pg_conn:
        for table in tables_to_check:
            get_rows_count_assertion(
                table_name=table,
                sqlite_conn=sqlite_conn,
                pg_conn=pg_conn,
                schema_name=pg_schema,
            )
            get_table_data_equality_assertion(
                table_name=table,
                sqlite_conn=sqlite_conn,
                pg_conn=pg_conn,
                schema_name=pg_schema,
            )
