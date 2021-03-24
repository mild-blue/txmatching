--
-- file: txmatching/database/db_migrations/0016.add-internal-medical-id.sql
-- depends: 0015.add-default-configuration-id
--

-- migrate donor hla_typing
ALTER TABLE recipient
    ADD COLUMN internal_medical_id TEXT default NULL;

ALTER TABLE donor
    ADD COLUMN internal_medical_id TEXT default NULL;
