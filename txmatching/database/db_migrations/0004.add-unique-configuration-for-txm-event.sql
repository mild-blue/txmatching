--
-- file: txmatching/database/db_migrations/0002.drop-unique-recipient-antibodies.sql
-- depends: 0001.initial-schema
--

ALTER TABLE config
    ADD CONSTRAINT  uq_config_txm_event_id UNIQUE (txm_event_id);

ALTER TABLE pairing_result
    ADD CONSTRAINT  uq_pairing_result_config_id UNIQUE (config_id);
