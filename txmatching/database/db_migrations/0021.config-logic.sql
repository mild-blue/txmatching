--
-- file: txmatching/database/db_migrations/0020.add-txm-event-state.sql
-- depends: 0019.add-and-remove-missing-hla-code-processing-result
-- TODOO: rename
--


ALTER TABLE config
DROP
COLUMN patients_hash;

DELETE
FROM pairing_result;

ALTER TABLE pairing_result
    ADD COLUMN patients_hash bigint not null default 0;

ALTER TABLE pairing_result
    RENAME COLUMN config_id TO original_config_id;
