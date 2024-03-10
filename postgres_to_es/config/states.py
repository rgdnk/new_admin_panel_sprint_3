# Standard Library
import abc
from typing import (
    Any,
    Dict,
    Optional,
)

# Third Party
from redis import Redis
from tenacity import retry

# First Party
from config.etl_config import (
    RETRY_CONFIG,
    RedisConfig,
    RedisConfiguration,
)


class BaseStorage(abc.ABC):
    """Абстрактное хранилище состояния.

    Позволяет сохранять и получать состояние.
    Способ хранения состояния может варьироваться в зависимости
    от итоговой реализации. Например, можно хранить информацию
    в базе данных или в распределённом файловом хранилище.
    """

    @abc.abstractmethod
    def save_state(self, state: Dict[str, Any]) -> None:
        """Сохранить состояние в хранилище."""

    @abc.abstractmethod
    def retrieve_state(self) -> Dict[str, Any]:
        """Получить состояние из хранилища."""


class RedisState:
    """Класс для работы с состояниями."""

    def __init__(self, redis_conn: Optional[Redis] = None) -> None:
        self._redis_conn = redis_conn

    @property
    def redis_connection(self) -> Redis:
        if not self._redis_conn:
            self._redis_conn = Redis(
                host=RedisConfiguration.host,
                port=RedisConfiguration.port,
            )
        return self._redis_conn  # type: ignore

    @retry(**RETRY_CONFIG)
    def set_state(self, key: str, value: Any) -> None:
        """Установить состояние для определённого ключа."""
        self.redis_connection.set(key, value.encode())

    def get_state(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Получить состояние по определённому ключу."""
        data = self.redis_connection.get(key)
        if data:
            return data.decode()
        return default
