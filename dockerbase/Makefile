build-conda-base:
	docker build -f Dockerfile.conda-base -t "mildblue/txmatching-conda-base:${VERSION}" .

publish-conda-base: build-conda-base
	docker push "mildblue/txmatching-conda-base:${VERSION}"

build-conda-dependencies: build-conda-base
	docker build -f Dockerfile.conda-dependencies -t "mildblue/txmatching-conda-dependencies:${VERSION}" ../

publish-conda-dependencies: build-conda-dependencies
	docker push "mildblue/txmatching-conda-dependencies:${VERSION}"

build: build-conda-base build-conda-dependencies

# call with VERSION=<version>
publish: publish-conda-base publish-conda-dependencies