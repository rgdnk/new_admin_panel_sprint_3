.PHONY: up-test up-prod down-test down-prod swagger-run swagger-stop swagger-delete add-data test-logs redis es

up-test:
	docker-compose -f docker-compose.test.yml up --build -d

up-prod:
	docker-compose -f docker-compose.override.yml up --build -d

down-test:
	docker-compose -f docker-compose.test.yml down

down-prod:
	docker-compose -f docker-compose.override.yml down

swagger-run:
	docker run -p 9595:8080 --name swagger -v ./django_api/openapi.yaml:/swagger.yaml -e SWAGGER_JSON=/swagger.yaml swaggerapi/swagger-ui

swagger-stop:
	docker stop swagger

swagger-delete:
	docker rm -f swagger

add-data:
	python3 sqlite_to_postgres/load_data.py

test-logs:
	docker-compose -f docker-compose.test.yml logs
