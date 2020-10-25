--
-- file: txmatching/database/db_migrations/0004.add-unique-configuration-for-txm-event.sql
-- depends: 0003.parsing-errors
--

TRUNCATE TABLE config RESTART IDENTITY CASCADE;
TRUNCATE TABLE pairing_result RESTART IDENTITY CASCADE;

ALTER TABLE config
    ADD CONSTRAINT uq_config_txm_event_id UNIQUE (txm_event_id);

ALTER TABLE pairing_result
    ADD CONSTRAINT uq_pairing_result_config_id UNIQUE (config_id);
