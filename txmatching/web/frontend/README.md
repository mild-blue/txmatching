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

### Angular

In Terminal or Command line run:

```
npm install -g @angular/cli
```

It will globally install Angular on your machine.

### OpenAPI Generator

We use _openapi-generator_ to automatically generate TS files from swagger. Please run:

```
npm install -g @openapitools/openapi-generator-cli
```

---

Note: Navigate to `txmatching/web/frontend` before running the commands bellow.

## Before starting dev server

After downloading a new version of frontend app, you need to run `npm install -g` in case there is a need to install additional modules.

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
