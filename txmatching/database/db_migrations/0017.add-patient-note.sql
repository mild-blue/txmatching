--
-- file: txmatching/database/db_migrations/0017.add-patient-note.sql
-- depends: 0016.add-internal-medical-id
--

ALTER TABLE recipient
    ADD COLUMN note TEXT NOT NULL default '';

ALTER TABLE donor
    ADD COLUMN note TEXT NOT NULL default '';
