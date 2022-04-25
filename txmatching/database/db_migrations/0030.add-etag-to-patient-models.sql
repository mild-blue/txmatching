--
-- file: txmatching/database/db_migrations/0030.add-etag-to-patient-models.sql
-- depends: 0029.add-second-belgium-transplant-center
--

ALTER TABLE donor
    ADD COLUMN etag BIGINT NOT NULL DEFAULT 1;

ALTER TABLE recipient
    ADD COLUMN etag BIGINT NOT NULL DEFAULT 1;
