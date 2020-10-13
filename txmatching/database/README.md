# DB Migrations via Yoyo

Because we are using migrations via RAW SQL, we are using [Yoyo](https://ollycope.com/software/yoyo/latest/) library.
There are prepared migration commands in main `Makefile`.

## Create DB migration

1. Create new file in folder `txmatching/database/db_migration` in format `[MIGRATION_NUMBER.MIGRATION_NAME].sql`,
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

Note: migration name, e.g., `[MIGRATION_NUMBER.MIGRATION_NAME]` must be unique.


1. Execute migration via `make migrate-db` with required environment variables described in Makefile next to this task.
   So you have to create `.env.pub`based on `.env.teplate` file next to the Makefile and fill it in with proper environment
   variables.
