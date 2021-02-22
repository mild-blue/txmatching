include .env

build-conda-base:
	docker build -f Dockerfile.conda-base -t "ghcr.io/mild-blue/txmatching-conda-base:${VERSION}" .

publish-conda-base: build-conda-base
	echo ${PAT_TOKEN} | docker login ghcr.io -u ${GITHUB_USER} --password-stdin
	docker push "ghcr.io/mild-blue/txmatching-conda-base:${VERSION}"

build-conda-dependencies: build-conda-base
	docker build -f Dockerfile.conda-dependencies -t "ghcr.io/mild-blue/txmatching-conda-dependencies:${VERSION}" ../

publish-conda-dependencies: build-conda-dependencies
	echo ${PAT_TOKEN} | docker login ghcr.io -u ${GITHUB_USER} --password-stdin
	docker push "ghcr.io/mild-blue/txmatching-conda-dependencies:${VERSION}"

build: build-conda-base build-conda-dependencies

# call with VERSION=<version>
publish: publish-conda-base publish-conda-dependencies
