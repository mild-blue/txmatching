--
-- file: txmatching/database/db_migrations/0022.config-logic.sql
-- depends: 0021.add-missing-hla-code-processing-result
--


ALTER TABLE config
DROP
COLUMN patients_hash;

DELETE
FROM pairing_result;

ALTER TABLE pairing_result
    ADD COLUMN patients_hash bigint not null;

ALTER TABLE pairing_result
    RENAME COLUMN config_id TO original_config_id;
