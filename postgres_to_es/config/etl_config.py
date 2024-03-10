# Standard Library
import logging
from enum import Enum

# Third Party
import tenacity
from pydantic import Field
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)


logger = logging.getLogger(__name__)


class PostgresConnectParameters(BaseSettings):
    dbname: str = Field(alias="POSTGRES_DB")
    user: str = Field(alias="POSTGRES_USER")
    password: str = Field(alias="POSTGRES_PASSWORD")
    host: str = Field(alias="POSTGRES_HOST")
    port: int = Field(alias="POSTGRES_PORT")

    model_config = SettingsConfigDict(
        env_file="etl.env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


class ESConfigSettings(BaseSettings):
    http_schema: str = Field(alias="ELASTICSEARCH_SCHEMA")
    host: str = Field(alias="ELASTICSEARCH_HOST")
    port: int = Field(alias="ELASTICSEARCH_PORT")

    model_config = SettingsConfigDict(
        env_file="etl.env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


class ETLProcessConfig(BaseSettings):
    batch_size: int = Field(alias="BATCH_SIZE")
    frequency: int = Field(alias="FREQUENCY")

    model_config = SettingsConfigDict(
        env_file="etl.env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


class TenacityRetryConfig(BaseSettings):
    max_retries: int = Field(alias="MAX_RETRIES")
    max_wait: int = Field(alias="MAX_WAIT")
    jitter: int = Field(alias="JITTER")

    model_config = SettingsConfigDict(
        env_file="etl.env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


class RedisConfig(BaseSettings):
    host: str = Field(alias="REDIS_HOST")
    port: int = Field(alias="REDIS_PORT")


PGConfig = PostgresConnectParameters()
ESConfig = ESConfigSettings()
ETLConfig = ETLProcessConfig()
TenacityConfig = TenacityRetryConfig()
RedisConfiguration = RedisConfig()

RETRY_CONFIG = {
    "wait": tenacity.wait_exponential_jitter(
        initial=1,
        max=TenacityConfig.max_wait,
        jitter=TenacityConfig.jitter,
    ),
    "stop": tenacity.stop_after_attempt(TenacityConfig.max_retries),
    "before": tenacity.before_log(logger=logger, log_level=logging.INFO),
}


class ETLIndexes(str, Enum):
    movies = "movies"
