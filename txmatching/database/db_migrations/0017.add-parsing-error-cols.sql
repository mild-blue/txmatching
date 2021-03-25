--
-- file: txmatching/database/db_migrations/0017.add-parsing-error-cols.sql
-- depends: 0016.add-internal-medical-id
--

ALTER TABLE parsing_error
    ADD COLUMN message TEXT default '';

ALTER TABLE parsing_error
    ADD COLUMN medical_id TEXT default NULL;
