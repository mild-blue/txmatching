# Docker Compose Deployment

## Base Setup

1. Create `.env` file based on `.env.template` file and set proper variables.
1. Copy `redeploy-backend.sh` file and set `GIT_TOKEN` variable in this file.
1. Copy `docker-compose.yml` file.

## Start All
1. For the first time, just get proper latest Git tag and call `BACKEND_TAG=LATEST_TAG_VALUE docker-compose -f docker-compose.yml up -d`

## Redeploy Backend
1. Run `. ./redeploy-backend.sh` - proper backend version will be set automatically from the latest Git repository tag.

## Access DB from Localhost via Port-forwarding
1. `ssh -L 1234:localhost:5432 txmatch-USERNAME@172.17.3.14` will make DB accessible on `localhost:1234`.

## Useful Commands

1. Deploy all: `docker-compose -f docker-compose.yml up -d`
1. Destroy all: `docker-compose -f docker-compose.yml down`
1. Stop service: `docker-compose -f docker-compose.yml stop SERVICE_NAME`
1. Forward DB to localhost port 1234: `ssh -L 1234:localhost:5432 txmatch-USERNAME@172.17.3.14`
