# Standard Library
from dataclasses import astuple

# Third Party
import psycopg2
from psycopg2.extras import execute_values
from psycopg2.sql import SQL


class PGSaver:

    def __init__(self, connection, schema, page_size=100) -> None:
        self.connection = connection
        self.schema = schema
        self.page_size = page_size

    def create_schema(self, schema) -> bool:
        query = SQL(
            f"CREATE SCHEMA IF NOT EXISTS {schema}",
        )
        with self.connection.cursor(
            cursor_factory=psycopg2.extras.NamedTupleCursor,
        ) as cur:
            try:
                cur.execute(query)
                return True
            except psycopg2.Error:
                return False

    def save_all_data(self, table_name, data, column_names):
        cursor = self.connection.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor)

        values_to_insert = [astuple(object) for object in data]
        query = SQL(
            f"INSERT INTO {self.schema}.{table_name} ({column_names}) values %s "
            f"ON CONFLICT (id) DO NOTHING",
        )
        if self.create_schema(self.schema):
            try:
                execute_values(
                    cursor,
                    query,
                    values_to_insert,
                    page_size=self.page_size,
                )
                self.connection.commit()
            except psycopg2.Error:
                self.connection.rollback()
                raise Exception(
                    f"Error while inserting into table {table_name}, don't forget to use logger next time",
                )
