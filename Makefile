# creates environment from the file
conda-create:
	conda env create -f conda.yml

# exports all changes made localy - then one must copy the changes to conda.yml
conda-export:
	conda env export --from-history

# updates environment when some changes were applied to the file
conda-update:
	conda env update --file conda.yml  --prune

docker-build:
	docker build -t datavid19/kidney-exchange .

# Depoyment
local-redeploy:
	git pull; \
	docker-compose stop backend || true; \
	docker-compose rm backend || true; \
	docker-compose -f docker-compose.prod.yml up -d --build backend;

redeploy:
	git pull; \
	docker-compose pull datavid19/kidney-exchange:latest; \
	docker-compose stop backend || true; \
	docker-compose rm backend || true; \
	docker-compose -f docker-compose.prod.yml up -d backend;
