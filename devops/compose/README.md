# Docker Compose Deployment

## Base Setup

1. Create `.env` file based on `.env.template` file.
2. Copy `redeploy-backend.sh` file.
2. Copy `docker-compose.template.yml.sh` file.

## Start All
1. For the first time, just create file `docker-compose.yml` based on `docker-compose.template.yml` and replace `TAG` with required value.
1. Run `docker-compose -f docker-compose.yml up -d`

## Redeploy Backend
1. Run `. ./redeploy-backend.sh`
