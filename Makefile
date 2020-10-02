include .env.pub

CONDA_ENV=txmatching

# creates environment from the file
conda-create:
	conda env create -f conda.yml --name $(CONDA_ENV)

# exports all changes made locally - then one must copy the changes to conda.yml
conda-export:
	conda env export --from-history

# updates environment when some changes were applied to the file
conda-update:
	conda env update --file conda.yml --prune --name $(CONDA_ENV)

conda-activate:
	conda activate $(CONDA_ENV)

# builds docker image
docker-build:
	docker build -t mildblue/txmatching .

# start up the db
db:
	docker-compose up -d db

# run app locally on bare metal with debug flask and hot reload enabled
run:
	export FLASK_APP=txmatching.web.app:app; \
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
# deployment to prod with local build
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
	docker pull mildblue/txmatching:latest; \
	docker-compose -f docker-compose.prod.yml stop backend || true; \
	docker-compose -f docker-compose.prod.yml rm -f backend || true; \
	docker-compose -f docker-compose.prod.yml up -d backend;

# get logs from the running service
logs:
	docker-compose -f docker-compose.prod.yml logs --follow backend

setup-non-empty-db:
	docker-compose stop db || true
	docker-compose rm -f db || true
	docker volume rm txmatching_txmatching-postgres || true
	docker-compose up -d db
	sleep 2
	PGPASSWORD=${POSTGRES_PASSWORD} psql -h localhost -p 5432 -U ${POSTGRES_USER} -d ${POSTGRES_DB} -a -f ./txmatching/database/db_migrations/V1_schema.sql
	cd tests/test_utilities; PYTHONPATH=../..:$PYTHONPATH python populate_db.py
	PGPASSWORD=${POSTGRES_PASSWORD} psql -h localhost -p 5432 -U ${POSTGRES_USER} -d ${POSTGRES_DB} -a -f ./tests/test_utilities/patient_data_2020_07_obfuscated.sql

clean-db:
	PGPASSWORD=${POSTGRES_PASSWORD} psql -h localhost -p 5432 -U ${POSTGRES_USER} -d ${POSTGRES_DB} -a -f ./tests/test_utilities/clean_db.sql

lint:
	pylint txmatching

test:
	cd tests; export PYTHONPATH=../; python -m unittest discover -s . -t .

check: lint test

build-fe:
	cd txmatching/web/frontend; npm install && npm run build

build-fe-prod:
	cd txmatching/web/frontend; npm install && npm run build-prod

run-fe:
	cd txmatching/web/frontend; npm run start

rebuild: conda-update build-fe