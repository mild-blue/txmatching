--
-- file: txmatching/database/db_migrations/0010.add-patients-hash.sql
-- depends: 0009.drop-unique-uploaded-data
--

ALTER TABLE config
    ADD COLUMN patients_hash bigint not null default 0
