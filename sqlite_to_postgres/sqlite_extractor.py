# Standard Library
import sqlite3
from contextlib import (
    closing,
    contextmanager,
)


class SQLiteExtractor:
    def __init__(self, connect, page_size) -> None:
        self.connect = connect
        self.page_size = page_size

    @contextmanager
    def conn_context(self):
        conn = self.connect
        try:
            yield conn
            conn.commit()
        except sqlite3.OperationalError:
            raise Exception(
                f"Connection not started, here is the error: {sqlite3.OperationalError}",
            )

    def get_table_names_from_sqlite(self):
        with self.conn_context() as conn:
            curs = conn.cursor()
            curs.execute("SELECT name FROM sqlite_master WHERE type='table'")
            table_names = [row[0] for row in curs.fetchall()]
        if table_names is not None:
            return table_names

    def get_sqlite_data(self, table_name, columns, page_size, query=None):
        with self.conn_context() as conn:
            curs = conn.cursor()
            curs.execute(f"select {columns} from {table_name};")
            # Переписать на fetchmany() БД с индексами, ключами и констрейнтами - переписать вообще всё :)
            # Зато сделана бонусная задача на батчевую заливку.
            while True:
                data = curs.fetchmany(page_size)
                if not data:
                    break
                yield data
