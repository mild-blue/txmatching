# Docker Base Images

This folder contains two docker images, that are used as a base for the TXMatching.

## Updating images
When it is necessary to update the base image, execute `make publish VERSION=<new-version>`
and then update [Github Actions](../.github/workflows/pr.yml) pipeline and
[TXM Dockerfile](../Dockerfile) with correct (the new) version.
Example:
```
make publish VERSION=1.0.0
```

### Dockerfile.conda-base
The base OS image for the project, it contains necessary system libraries 
and the installation of the conda.

Note that in order to be able to build this image, one must have the Miniconda shell script
downloaded as well. The script is registered as Git LFS, thus not downloaded by default.
To install the Git LFS see [guide](https://github.com/git-lfs/git-lfs/wiki/Installation) and 
to download the miniconda shell script execute
```bash
git lfs pull Miniconda3-4.8.5-Linux-x86_64.sh
```

### Dockerfile.conda-dependencies
Image based on the `Dockerfile.conda-base` contains installed dependencies from the `conda.yml`.
It can be directly used as a runtime for the project or as a base for executing the tests.


```
NOTE: `Dockerfile.conda-dependencies` depends on `Dockerfile.conda-base`, so do not forget to update version
in `Dockerfile.conda-dependencies` file.
```

### GH pipeline

There exist GH pipeline for building these images (see `/github/workflows/base-images.yml`).
To build new version(s), do following steps:

- Update version in `.env.template`.
- Update version in `Dockerfile.conda-dependencies`.
- Push changes and run GH action.
- Do not forget to update version in main `Dockerfile`.