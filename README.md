# txmatching

Solver for kidney pair donation matching problems.

## About

This is a tool that allows kidney pair donation centre to find the best possible matching from a pool of patients.

It consists of backend written in Python and an Angular frontend.

## How to run the app locally 

The project runs on MacOs (not M1 chip), Linux and Windows. To run on Windows you need Docker and WSL2 as we are using [gunicorn](https://gunicorn.org/) which does not run on Windows. 

### Prepare Frontend
In order to build Frontend for the app one must run `make build-fe`.
If it does not work, you might have some dependencies missing.
For details see [README.md](txmatching/web/frontend/README.md).

One must do that every time when something was changed in the FE code in order to have up to date FE.

What this does is that it builds FE code to `txmatching/web/frontend/dist/frontend` directory,
where it is picked up by the Flask.

In case npm can't find some of packages and you get this error:
```
ENOENT: no such file or directory, chmod '.../node_modules/...`
```
try to remove `node_modules` folder from `txmatching/web/frontend/`, run `npm cache clean -f` and then run the command again.



### Prepare Backend
Backend is written in Python. We are using [conda](https://docs.conda.io/en/latest/miniconda.html) for
dependency management. To be able to run the project you must have it istalled.

After you have conda ready and setup. Execute `make conda-create` which creates Conda env for you.

Finally, activate the environment with `conda activate txmatching`

#### Install wkhtmltopdf

For pdf generation, a [wkhtmltopdf](https://wkhtmltopdf.org/downloads.html) is required to be installed.

```
sudo apt update
sudo apt install wget xfonts-75dpi
cd /tmp
```

`wget https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6-1/wkhtmltox_0.12.6-1.focal_amd64.deb` (choose your version)

`sudo dpkg -i wkhtmltox_0.12.6-1.focal_amd64.deb` (of the correct version that you want to install)

`wkhtmltopdf --version` (to check that it worked)


### Prepare Database
You need to have docker installed. And you need to have activated environment from the previous step.

After that simply run `make setup-small-non-empty-db`

This runs postgres database in docker that has already some data inside.

### Run the app
 Simply run `make run`. This should start the app at localhost:8080. To log in use credentials `admin@example.com` and
 password `admin`

## Swagger
We have a swagger UI running on `/doc/` route (so for example, `localhost:8080/doc/`).
How to use it and some useful info [here on doc](https://flask-restx.readthedocs.io/en/latest/swagger.html).

The swagger is also in the project. It is generated in `txmatching/web/swagger.yaml`. We always test that it is up to date
and in case any changes are made, one needs to regenerated it using `local_testing_utilities/generate-swagger.py` by 
running `make generate-swagger-file` command.

We also automatically generate TypeScript files that are used by FE. These files are generated from the swagger file
using `openapi-generator-cli` tool. To install this tool, please refer to [README.md](txmatching/web/frontend/README.md).

You can automatically generate both swagger file and TS files by running `make generate-swagger-all`.

You should be able to create user with some rights to some events. Also you should be able to create an txm event
with duplicate patients from another event via the swagger endpoints.

## Development

### Dependencies Management
We are using `conda` for managing dependencies.

#### Adding New dependencies
To add new package put `<package>` to `conda.yml` and execute `make conda-update`.
Please try to install specific version which you put to `conda.yml` in order to guarantee that whole team has the same
versions of packages.
Try to put package to `dependencies` part of yaml, that are the packages installed from conda repository,
if the package is not in the conda repo, put it in the `pip` part of yaml.

**Note** that before the PR with new dependencies is submitted, one must build and publish new version of the
`mildblue/txmatching-conda-dependencies` docker image.
To do that, go to `dockerbase` directory, login to container registry and see further information
in the related [README](dockerbase/README.md).

#### Updating Packages
when someone updates and you pull new version from git do the following:
```
make conda-update
```

### Git Hooks
there are some githooks in this project. It is advised to use them. After installing dependencies in conda it should be enough to run
```
pre-commit install
```
then everytime you commit it first fails in case there were some changes done by the pre-commit script.
If you recommit it will pass, because all the needed changes were done. Its especially so we do not push notebooks
that would contain data to git.

### Application Configuration
Right now Flask web server tries to load configuration from the environment
with fallback to loading from [`local_config.py`](txmatching/web/local_config.py).
All current configuration can be found [here](txmatching/configuration/app_configuration/application_configuration.py).
To obtain configuration in the code, one should call `get_application_configuration()`
 from [application_configuration.py](txmatching/configuration/app_configuration/application_configuration.py).

### Testing
To run unittests use `make test` command. `make check` command runs linter and unittests altogether.
