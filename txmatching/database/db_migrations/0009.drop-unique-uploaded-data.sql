--
-- file: txmatching/database/db_migrations/0009.drop-unique-uploaded-data.sql
-- depends: 0008.drop-unique-config-per-txm-event
--


ALTER TABLE uploaded_data
DROP CONSTRAINT uq_uploaded_data_txm_event_id_user_id;
