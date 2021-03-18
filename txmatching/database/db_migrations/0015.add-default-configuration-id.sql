--
-- file: txmatching/database/db_migrations/0015.add-default-configuration-id.sql
-- depends: 0013.remove_configuration
--


ALTER TABLE txm_event
    ADD COLUMN default_config_id BIGINT;
