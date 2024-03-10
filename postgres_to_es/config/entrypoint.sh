#!/usr/bin/env bash

readonly cmd="$*"

while ! nc -z elastic 9200; do
      sleep 20
      echo "Elasticsearch not ready"
done

echo "Elasticsearch is ready"

curl -XPUT http://elastic:9200/movies -H 'Content-Type: application/json' -d @/movies.json

echo "Elasticsearch movie index was created"

exec $cmd