#!/usr/bin/env bash

readonly cmd="$*"

export SCHEMA=${ELASTICSEARCH_SCHEMA}
export HOST=${ELASTICSEARCH_HOST}
export PORT=${ELASTICSEARCH_PORT}

# Я не пользуюсь этим скриптом, отправляю curl со схемой в отдельном контейнере docker compose
# Поправил, как смог, обещаю подучить bash в будущем!
while ! nc -z ${HOST} ${PORT}; do
      sleep 20
      echo "Elasticsearch not ready"
done

echo "Elasticsearch is ready"

curl -XPUT ${SCHEMA}://${HOST}:${PORT}/movies -H 'Content-Type: application/json' -d @/movies.json

echo "Elasticsearch movie index was created"

exec $cmd