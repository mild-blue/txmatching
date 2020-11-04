build-conda-base:
	docker pull mildblue/txmatching-conda-base:latest || true;
	docker build -f Dockerfile.conda-base -t mildblue/txmatching-conda-base:latest .

publish-conda-base: build-conda-base
	docker push mildblue/txmatching-conda-base:latest

build-conda-dependencies: build-conda-base
	docker pull mildblue/txmatching-conda-dependencies:latest || true;
	docker build -f Dockerfile.conda-dependencies -t mildblue/txmatching-conda-dependencies:latest ../

publish-conda-dependencies: build-conda-dependencies
	docker push mildblue/txmatching-conda-dependencies:latest

build: build-conda-base build-conda-dependencies

publish: build