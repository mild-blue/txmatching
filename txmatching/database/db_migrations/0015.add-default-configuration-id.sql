--
-- file: txmatching/database/db_migrations/0015.add-default-configuration-id.sql
-- depends: 0014.add_new_error_type
--


ALTER TABLE txm_event
    ADD COLUMN default_config_id BIGINT;
