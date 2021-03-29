--
-- file: txmatching/database/db_migrations/0017.add-parsing-error-cols.sql
-- depends: 0016.add-internal-medical-id
--

ALTER TABLE parsing_error
    ADD COLUMN message TEXT default '';

ALTER TABLE parsing_error
    ADD COLUMN medical_id TEXT default NULL;

ALTER TABLE parsing_error
    ADD COLUMN txm_event_id BIGINT default NULL;

ALTER TABLE parsing_error
    ADD CONSTRAINT fk_parsing_error_txm_event_id FOREIGN KEY (txm_event_id) REFERENCES txm_event(id) ON DELETE CASCADE;

ALTER TYPE HLA_CODE_PROCESSING_RESULT_DETAIL ADD VALUE 'MFI_PROBLEM';
ALTER TYPE HLA_CODE_PROCESSING_RESULT_DETAIL ADD VALUE 'OTHER_PROBLEM';
