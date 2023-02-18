--
-- file: txmatching/database/db_migrations/0037.add-attribute-to-hla-antibody.sql
-- depends: 0036.add-attribute-to-txm-event-base
--

ALTER TABLE hla_antibody_raw ADD COLUMN second_raw_code TEXT;
