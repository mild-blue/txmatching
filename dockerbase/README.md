# Docker base images

This folder contains two docker images, that are used as a base for the TXMatching.

### Dockerfile.conda-base
The base OS image for the project, it contains necessary system libraries 
and the installation of the conda.

### Dockerfile.conda-dependencies
Image based on the `Dockerfile.conda-base` contains installed dependencies from the `conda.yml`.
It can be directly used as a runtime for the project or as a base for executing the tests.