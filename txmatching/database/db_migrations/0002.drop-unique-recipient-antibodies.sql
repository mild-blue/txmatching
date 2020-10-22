--
-- file: txmatching/database/db_migrations/0002.drop-unique-recipient-antibodies.sql
-- depends: 0001.initial-schema
--

ALTER TABLE recipient_hla_antibodies
    DROP CONSTRAINT uq_recipient_hla_antibodies_code_recipient_id;
