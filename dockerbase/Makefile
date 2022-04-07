include .env

BASE_IMAGE_NAME="ghcr.io/mild-blue/txmatching-conda-base:${VERSION}"
DEPENDENCIES_IMAGE_NAME="ghcr.io/mild-blue/txmatching-conda-dependencies:${VERSION}"


build-conda-base:
	docker build -f Dockerfile.conda-base -t "$(BASE_IMAGE_NAME)" .

publish-conda-base: build-conda-base
	echo ${PAT_TOKEN} | docker login ghcr.io -u ${GITHUB_USERNAME} --password-stdin
	docker push "$(BASE_IMAGE_NAME)"

build-conda-dependencies: build-conda-base
	docker build -f Dockerfile.conda-dependencies -t "$(DEPENDENCIES_IMAGE_NAME)" ../

publish-conda-dependencies: build-conda-dependencies
	echo ${PAT_TOKEN} | docker login ghcr.io -u ${GITHUB_USERNAME} --password-stdin
	docker push "$(DEPENDENCIES_IMAGE_NAME)"

# Call with VERSION=<version>.
build: build-conda-base build-conda-dependencies

# Call with VERSION=<version>.
publish: publish-conda-base publish-conda-dependencies

# Call with VERSION=<version>, used for GH pipeline
publish-in-pipeline:
	docker build -f Dockerfile.conda-base -t "$(BASE_IMAGE_NAME)" .
	docker push "$(BASE_IMAGE_NAME)"
	docker build -f Dockerfile.conda-dependencies -t "$(DEPENDENCIES_IMAGE_NAME)" ../
	docker push "$(DEPENDENCIES_IMAGE_NAME)"
