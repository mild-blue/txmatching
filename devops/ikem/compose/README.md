# Docker Compose Deployment

1. Connect into IKEM VPN.
1. Connect into server `172.17.3.14` with your user credentials stored in [Bitwarden](https://vault.bitwarden.com/#/vault).
1. Switch to *root* user via `su root`. Password is stored in your home directory and should be stored in [Bitwarden](https://vault.bitwarden.com/#/vault).

## Base Setup

1. Create a folder on server, e.g., `/srv/txmatching/deployment`.
1. Copy `redeploy-backend.sh` file into the folder `/srv/txmatching/deployment` and set `GIT_TOKEN` variable in this file.

## Start All
1. For the first time go into `/srv/txmatching/deployment` and call `./redeploy-backend.sh`.

## Redeploy Backend
1. Go into `/srv/txmatching/deployment` and call `./redeploy-backend.sh`.

## Access DB from Localhost via Port-forwarding
1. `ssh -L 1234:localhost:5432 txmatch-USERNAME@172.17.3.14` will make DB accessible on `localhost:1234`.

## DB Migration from local machine in emergency cases

1. Connect via `ssh -L 1234:localhost:5432 txmatch-USERNAME@172.17.3.14` to server.
1. Execute `make migrate-db-prod` in root directory. Credentials are stored in [Bitwarden](https://vault.bitwarden.com/#/vault).

## Useful Commands

1. Deploy all: `docker-compose -f docker-compose.yml up -d`
1. Destroy all: `docker-compose -f docker-compose.yml down`
1. Stop service: `docker-compose -f docker-compose.yml stop SERVICE_NAME`
1. Forward DB to localhost port 1234: `ssh -L 1234:localhost:5432 txmatch-USERNAME@172.17.3.14`
1. Show running Docker containers: `docker ps`.
1. Show service logs: `docker logs --follow SERVICE_NAME`.
