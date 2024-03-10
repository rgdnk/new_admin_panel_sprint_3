# Standard Library
from datetime import datetime
from typing import (
    Iterator,
    List,
    Optional,
    Tuple,
)

# Third Party
from data_transformer import PGDataTransformer
from elasticsearch import Elasticsearch
from es_loader import ESLoader
from postgres_extractor import PGExtractor

# First Party
from config.etl_config import (
    ESConfigSettings,
    ETLConfig,
    ETLIndexes,
    PostgresConnectParameters,
)
from config.sql_queries import get_query_by_index
from config.states import RedisState


class ETL:
    def __init__(
        self,
        postgres_settings: PostgresConnectParameters,
        state: RedisState,
        es_conn: Elasticsearch,
        es_config: Optional[ESConfigSettings],
    ) -> None:
        self._postgres_settings = postgres_settings
        self._state = state
        self._es_conn = es_conn
        self._es_config = es_config
        self._extractor = PGExtractor(self._postgres_settings)
        self._transformer = PGDataTransformer(self._state)
        self._loader = ESLoader(self._es_config, self._state, self._es_conn)

    def extract_data(
        self,
        index: str,
        query: str,
        itersize: int,
    ) -> Iterator[Tuple[dict, str]]:
        return self._extractor.get_data(index, query, itersize)

    def transform_data(
        self,
        index: str,
        data: Iterator[Tuple[dict, str]],
    ) -> Iterator[dict]:
        return self._transformer.transform_data_for_es(index, data)

    def load_data_to_es(self, index: str, data: Iterator[dict], itersize: int) -> None:
        return self._loader.upload_data_to_es(index, data, itersize)

    def run(self, indexes: ETLIndexes) -> None:
        for index in indexes:
            load_from = self._state.get_state(
                key=f"last_updated_in_{index}",
                default=str(datetime.min),
            )
            try:
                itersize = ETLConfig.batch_size
                query = get_query_by_index(index=index, load_from=load_from)
                extracted_data = self.extract_data(
                    index=index,
                    query=query,
                    itersize=itersize,
                )
            except ValueError:
                continue
            transformed_data = self.transform_data(index=index, data=extracted_data)
            self.load_data_to_es(index=index, data=transformed_data, itersize=itersize)
