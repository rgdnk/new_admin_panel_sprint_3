# Standard Library
import logging
import time

# Third Party
from elasticsearch import Elasticsearch

# First Party
from config.etl_config import (
    ESConfig,
    ESConfigSettings,
    ETLConfig,
    ETLIndexes,
    PostgresConnectParameters,
)
from config.states import RedisState
from etl import ETL


indexes = ETLIndexes
frequency = ETLConfig.frequency

if __name__ == "__main__":
    logger = logging.getLogger(__name__)

    etl = ETL(
        postgres_settings=PostgresConnectParameters,
        state=RedisState(),
        es_conn=Elasticsearch(
            [f"{ESConfig.http_schema}://{ESConfig.host}:{ESConfig.port}"],
        ),
        es_config=ESConfigSettings,
    )

    while True:
        logger.info("Starting sync...")
        try:
            etl.run(indexes=indexes)

        except ValueError as e:
            logger.error(e)
            Elasticsearch.transport.close()
            continue

        logger.info(f"Sleep for {frequency} seconds")
        time.sleep(frequency)
