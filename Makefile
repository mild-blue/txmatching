include .env.pub

# creates environment from the file
conda-create:
	conda env create -f conda.yml

# exports all changes made localy - then one must copy the changes to conda.yml
conda-export:
	conda env export --from-history

# updates environment when some changes were applied to the file
conda-update:
	conda env update --file conda.yml  --prune

# builds docker image
docker-build:
	docker build -t datavid19/kidney-exchange .

# start up the db
db:
	docker-compose up -d db

# run app localy on bare metal with debug flask and hot reload enabled
run:
	export FLASK_APP=kidney_exchange.web.app:app; \
	export FLASK_ENV=development; \
	export FLASK_DEBUG=true; \
	flask run --port=8080 --host=localhost

# run app in the docker-compose environment
dorun:
	docker-compose up backend

# rebuild and rerun backend in the docker
dorerun: docker-build
	docker-compose stop backend || true; \
	docker-compose rm -f backend || true; \
	docker-compose up backend;

# ------- following commands should be used only on production machine -------
# depoyment to prod with local build
build-redeploy:
	git pull; \
	docker-compose -f docker-compose.prod.yml stop backend || true; \
	docker-compose -f docker-compose.prod.yml rm -f backend || true; \
	docker-compose -f docker-compose.prod.yml up -d --build backend;

# deploy all services
deploy:
	docker-compose -f docker-compose.prod.yml up -d

# redeploy after image was updated, used by the pipeline
redeploy:
	git pull; \
	docker image prune -f; \
	docker pull datavid19/kidney-exchange:latest; \
	docker-compose -f docker-compose.prod.yml stop backend || true; \
	docker-compose -f docker-compose.prod.yml rm -f backend || true; \
	docker-compose -f docker-compose.prod.yml up -d backend;

# get logs from the running service
logs:
	docker-compose -f docker-compose.prod.yml logs --follow backend

setup-db-for-tests:
	docker stop kidney-exchange_db_1 || true
	docker rm kidney-exchange_db_1 || true
	docker volume rm  kidney-exchange_kidney-exchange-postgres || true
	docker-compose up -d db
	sleep 2
	PGPASSWORD=${POSTGRES_PASSWORD} psql -h localhost -p 5432 -U ${POSTGRES_USER} -d ${POSTGRES_DB} -a -f ./kidney_exchange/database/db_migrations/V1_schema.sql
	cd tests/data; PYTHONPATH=../..:$PYTHONPATH python prepare_db.py
	PGPASSWORD=${POSTGRES_PASSWORD} psql -h localhost -p 5432 -U ${POSTGRES_USER} -d ${POSTGRES_DB} -a -f ./tests/data/prepare_db.sql
