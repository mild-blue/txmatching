--
-- file: txmatching/database/db_migrations/0029.add-etag-to-patient-models.sql
-- depends: 0028.drop-medical-id-add-patient-db-id-in-parsing-error
--

ALTER TABLE donor
    ADD COLUMN etag bigint not null;

ALTER TABLE recipient
    ADD COLUMN etag bigint not null;
