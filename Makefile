include .env.local

CONDA_ENV=txmatching
ROOT_FOLDER_NAME=txmatching

SWAGGER_INPUT_FILE='txmatching/web/swagger/swagger.yaml'
SWAGGER_OUTPUT_DIR='/tmp/swagger-generated'
FE_GENERATED_DIR='txmatching/web/frontend/src/app/generated'

# creates environment from the file
conda-create:
	conda env create -f conda.yml --name $(CONDA_ENV)

# exports all changes made locally - then one must copy the changes to conda.yml
conda-export:
	conda env export --from-history

# updates environment when some changes were applied to the file
conda-update:
	conda env update --file conda.yml --prune --name $(CONDA_ENV)

# this actually does not work as make command, just copy paste it and run `conda activate txmatching`
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
	DEACTIVATE_DATETIME_IN_LOGGER=${DEACTIVATE_DATETIME_IN_LOGGER} \
	SHOW_USERS_ACTIONS=${SHOW_USERS_ACTIONS} \
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

setup-empty-db:
	docker-compose stop db || true
	docker-compose rm -f db || true
	docker volume rm $(ROOT_FOLDER_NAME)_txmatching-postgres || true
	docker-compose up -d db
	sleep 2
	make migrate-db

setup-non-empty-db:
	make setup-empty-db
	cd local_testing_utilities; PYTHONPATH=$${PYTHONPATH:-..} python populate_large_db.py

setup-small-non-empty-db:
	make setup-empty-db
	cd local_testing_utilities; PYTHONPATH=$${PYTHONPATH:-..} python populate_small_db.py

setup-multiple-donors-non-empty-db:
	make setup-empty-db
	cd local_testing_utilities; PYTHONPATH=$${PYTHONPATH:-..} python populate_db_multiple_donors.py

lint:
	pylint txmatching
	pylint local_testing_utilities

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

migrate-db:
	cd txmatching && PYTHONPATH=$${PYTHONPATH:-..} POSTGRES_USER=${POSTGRES_USER} POSTGRES_PASSWORD=${POSTGRES_PASSWORD} POSTGRES_DB=${POSTGRES_DB} POSTGRES_URL=${POSTGRES_URL} python database/migrate_db.py

generate-swagger-all: \
	generate-swagger-file \
	validate-swagger \
	generate-and-copy-ts-from-swagger

generate-swagger-file:
	PYTHONPATH=$${PYTHONPATH:-.} python local_testing_utilities/generate_swagger.py

validate-swagger:
	openapi-generator-cli validate -i $(SWAGGER_INPUT_FILE)

generate-and-copy-ts-from-swagger: \
	generate-ts-from-swagger \
	copy-generated-ts-to-fe

generate-ts-from-swagger:
	if [ -d $(SWAGGER_OUTPUT_DIR) ]; then \
	    rm -rf $(SWAGGER_OUTPUT_DIR); \
	fi;
	#npx @openapitools/openapi-generator-cli generate
	openapi-generator-cli generate \
		-i $(SWAGGER_INPUT_FILE) \
		-c 'txmatching/web/swagger-ts-generator.conf.json' \
		-g typescript-angular \
		-o $(SWAGGER_OUTPUT_DIR)/

copy-generated-ts-to-fe:
	if [ -d $(FE_GENERATED_DIR) ]; then \
	    git rm -rf --ignore-unmatch $(FE_GENERATED_DIR); \
	fi;
	mkdir -p $(FE_GENERATED_DIR)/model
	cp -r $(SWAGGER_OUTPUT_DIR)/model $(FE_GENERATED_DIR)
	echo "export * from './model/models';" > $(FE_GENERATED_DIR)/index.ts
	git add $(FE_GENERATED_DIR)

create-demo-event-json:
	echo "Type TXM event name data should be uploaded to:"; \
	read name; \
	echo $${name}; \
	for lang in CZE CAN IND; do \
	  	out=/tmp/demo_event_$${lang}.json ; \
		cat tests/resources/high_res_example_data/high_res_example_data_$${lang}.json \
			| sed "s/high_res_example_data/$${name}/" \
			> $${out} ; \
		echo $${out}: ;\
		cat $${out} ; \
	done; \

rerun: setup-non-empty-db run
