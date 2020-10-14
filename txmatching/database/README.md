# DB Migrations via Yoyo

Because we are using migrations via RAW SQL, we are using [Yoyo](https://ollycope.com/software/yoyo/latest/) library.
There are prepared migration commands in main `Makefile`.

## Create DB migration

1. Create new file in folder `txmatching/database/db_migration` in format `[MIGRATION-NUMBER.MIGRATION-NAME].sql`,
 e.g., `0001.initial-schema.sql`. This file should contain header in the form
```
--
-- file: txmatching/database/db_migrations/0001.initial-schema.sql
--
```
Optionally it can contain definition of dependencies in form
```
-- depends: 0001.initial-schema 0002.initial-schema-fixes
```

Note: migration name, e.g., `[MIGRATION-NUMBER.MIGRATION-NAME]` must be unique.


1. Execute migration via `make migrate-db` with required environment variables described in Makefile next to this task.
   So you have to create `.env.pub`based on `.env.teplate` file next to the Makefile and fill it in with proper environment
   variables.

## Production DB Migration

1. Login into IKEM VPN.
1. Execute `ssh -L 1234:localhost:5432 txmatch-USERNAME@172.17.3.14`.
1. Execute migration `cd txmatching && PYTHONPATH=$${PYTHONPATH:-..} POSTGRES_USER="txmatching-db-user" POSTGRES_PASSWORD="PASSWORD_FROM_BITWARDEN" POSTGRES_DB="txmatching" POSTGRES_URL="localhost:1234" python database/migrate_db.py`.
1. Check the DB to be sure.
