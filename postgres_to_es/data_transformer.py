# Standard Library
import logging
from typing import (
    Iterator,
    Tuple,
)

# First Party
from config.states import RedisState


logger = logging.getLogger(__name__)


class PGDataTransformer:
    def __init__(self, redis_state: RedisState) -> None:
        self._state = redis_state

    def transform_data_for_es(
        self,
        index,
        data: Iterator[Tuple[dict, str]],
    ) -> Iterator[dict]:
        last_updated = ""
        key = f"last_updated_in_{index}"

        logger.info("About to transform data for ES")
        for filmwork, modified_at in data:
            last_updated = modified_at
            yield filmwork

        if last_updated:
            self._state.set_state(key, last_updated)
