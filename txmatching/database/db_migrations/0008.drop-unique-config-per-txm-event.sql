--
-- file: txmatching/database/db_migrations/0008.drop-unique-config-per-txm-event.sql
-- depends: 0007.add-uploaded-files-table
--


ALTER TABLE config
DROP CONSTRAINT uq_config_txm_event_id;
