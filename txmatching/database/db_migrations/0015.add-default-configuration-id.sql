--
-- file: txmatching/database/db_migrations/0013.remove_configuration.sql
-- depends: 0012.add-user-to-allowed-event-table
-- TODOO
--


ALTER TABLE txm_event
    ADD COLUMN default_config_id BIGINT
    ADD CONSTRAINT fk_txm_event_default_config_id FOREIGN KEY (default_config_id) REFERENCES config(id);
