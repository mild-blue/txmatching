# Frontend

This project was generated with [Angular CLI](https://github.com/angular/angular-cli).

## GitHub pipeline failed in my PR

### Run prettier check

- you forgot to run `npm run prettier-format`
- plese run the command and commit changes

### Build check

- your project contains serious errors and can't be build

## Prerequisites

### Node.js and npm

npm is distributed with Node.js, which means that when you download Node.js, you automatically get npm installed on your computer.

[Download Node.js and npm](https://nodejs.org/en/)

Verify installation by running in Terminal or Command line:

```
node -v
```

and then:

```
npm -v
```

Make sure Node.js is of the latest versions (preferably 18.0+).

### Angular

In Terminal or Command line run:

```
npm install -g @angular/cli
```

(In Ubuntu based system you may need to run it with superuser rights)

It will globally install Angular on your machine.

### OpenAPI Generator

We use _openapi-generator_ to automatically generate TS files from swagger. Please run:

```
npm install -g @openapitools/openapi-generator-cli
```

(In Ubuntu based system you may need to run it with superuser rights)

Here comes very interesting part: openapi generator from npm comes in a quite old version
(at the time it is written) that is not very suitable us. Which shouldn't be a problem,
because it is updated during the first run of `make generate-swagger-all`,
but at least in Ubuntu it cannot be updated without superuser rights, so `make` commands will not work
(by some reason it is not possible to run `make` commands with superuser rights in Ubuntu).
So the part of the installation is to run any openapi-generator command with superuser rights.
For example: `sudo openapi-generator-cli validate -i txmatching/web/swagger/swagger.yaml ` - this should
update openapi-generator as well as validate swagger.yaml. Further runs of commands from Makefile related
to swagger should not have any problems.

---

Note: Navigate to `txmatching/web/frontend` before running the commands bellow.

## Before starting dev server

After downloading a new version of frontend app, you need to run `npm install` in case there is a need to install additional modules.

If you want to connect to different BE, create environment.local.ts and run `ng serve --configuration=dev`.

## Development server

Run `ng serve` for a dev server. You can alternatively run `npm run start` or use `make run-fe` in the root folder of the project.
Navigate to `http://localhost:4200/`. The app will automatically reload if you change any of the source files.

## Code scaffolding

Run `ng generate component component-name` to generate a new component. You can also use `ng generate directive|pipe|service|class|guard|interface|enum|module`.

## Build

Run `ng build` to build the project. The build artifacts will be stored in the `dist/` directory. Use the `--prod` flag for a production build.

## Running unit tests

Run `ng test` to execute the unit tests via [Karma](https://karma-runner.github.io).

## Running end-to-end tests

Run `ng e2e` to execute the end-to-end tests via [Protractor](http://www.protractortest.org/).

## Further help

To get more help on the Angular CLI use `ng help` or go check out the [Angular CLI README](https://github.com/angular/angular-cli/blob/master/README.md).
