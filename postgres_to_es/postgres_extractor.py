# Standard Library
import logging
from contextlib import closing
from typing import (
    Iterator,
    Tuple,
    Type,
)

# Third Party
import psycopg2
from psycopg2.extras import DictCursor
from tenacity import retry

# First Party
from config.etl_config import (
    RETRY_CONFIG,
    ETLIndexes,
    PostgresConnectParameters,
)
from config.etl_models import (
    BaseETLModel,
    MovieETLSchema,
)


logger = logging.getLogger(__name__)


class PGExtractor:
    def __init__(self, dsn: PostgresConnectParameters) -> None:
        self._dsn = dsn

    def get_data(
        self,
        index: str,
        query: str,
        itersize: int,
    ) -> Iterator[Tuple[dict, str]]:
        if index == ETLIndexes.movies:
            model = MovieETLSchema
            return self._make_data_request(model, query, itersize)

        raise ValueError(f"There is no extraction rule for index {index}")

    @retry(**RETRY_CONFIG)
    def _make_data_request(
        self,
        model: Type[BaseETLModel],
        query: str,
        itersize: int,
    ) -> Iterator[Tuple[dict, str]]:
        with closing(
            psycopg2.connect(
                **self._dsn().model_dump(),
                cursor_factory=DictCursor,
            )  # noqa
        ) as conn:  # noqa
            with conn.cursor() as cur:
                cur.itersize = itersize
                cur.execute(query)
                data = cur.fetchall()
                logger.info("About to extract data from Postgres")
            for row in data:
                instance = model(**row).model_dump()
                instance["_id"] = instance["id"]
                yield instance, str(row["modified"])
