# Standard Library
import logging
from typing import Iterator

# Third Party
from elasticsearch import (
    Elasticsearch,
    helpers,
)
from tenacity import retry

# First Party
from config.etl_config import (
    RETRY_CONFIG,
    ESConfigSettings,
)
from config.states import RedisState


logger = logging.getLogger(__name__)


class ESLoader:
    def __init__(
        self,
        config: ESConfigSettings,
        redis_state: RedisState,
        es_conn: Elasticsearch,
    ) -> None:
        self._config = config
        self._es_conn = es_conn
        self._state = redis_state

    @retry(**RETRY_CONFIG)
    def create_es_connection(self) -> Elasticsearch:
        if self._es_conn is None:
            self._es_conn = Elasticsearch(
                [
                    f"{self._config.http_schema}://{self._config.host}:{self._config.port}",
                ],
            )
            return self._es_conn

    @retry(**RETRY_CONFIG)
    def upload_data_to_es(
        self,
        index: str,
        data: Iterator[dict],
        itersize: int,
    ) -> None:

        rows, _ = helpers.bulk(
            client=self._es_conn,
            actions=data,
            index=index,
            chunk_size=itersize,
        )

        if rows == 0:
            logger.info(f"No updates for index {index}")
        else:
            logger.info(f"{rows} saved in index {index}")
