# DB Migrations via Alembic

Because we are using migrations via RAW SQL, migration process is little bit hacky that normally via generation from SQL Alchemy models.
There are prepared migration commands in main `Makefile`.

## Create DB migration and Execute it

1. Execute `make generate-new-db-migration` with required environment variables and REVISION and MESSAGE same as set for files.
   This generates new files `V[REVISION]_[MESSAGE]_.py` (do not change), `V[REVISION]_[MESSAGE]_up.sql` for new DB migration script and
   `V[REVISION]_[MESSAGE]_down.sql` for migration downgrade, i.e., revert commands.
1. Execute migration via `make migrate-db` with required environment variables.

## Downgrade DB migration

1. Execute migration via `make downgrade-db` with required environment variables.
