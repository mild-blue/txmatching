--
-- file: txmatching/database/db_migrations/0003.parsing-errors.sql
-- depends: 0002.drop-unique-recipient-antibodies
--

CREATE TYPE HLA_CODE_PROCESSING_RESULT_DETAIL AS ENUM (
    'SUCCESSFULLY_PARSED',
    'UNEXPECTED_SPLIT_RES_CODE',
    'MULTIPLE_SPLITS_FOUND',
    'UNKNOWN_TRANSFORMATION_TO_SPLIT',
    'UNPARSABLE_HLA_CODE'
    );

CREATE TABLE parsing_error
(
    id                                BIGSERIAL                         NOT NULL,
    txm_event_id                      BIGINT                            NOT NULL,
    hla_code                          TEXT                              NOT NULL,
    hla_code_processing_result_detail HLA_CODE_PROCESSING_RESULT_DETAIL NOT NULL,
    created_at                        TIMESTAMPTZ                       NOT NULL,
    updated_at                        TIMESTAMPTZ                       NOT NULL,
    deleted_at                        TIMESTAMPTZ,
    CONSTRAINT pk_parsing_error_id PRIMARY KEY (id),
    CONSTRAINT fk_parsing_error_upload_data_id FOREIGN KEY (txm_event) REFERENCES config (id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TRIGGER trg_parsing_error_set_created_at
    BEFORE INSERT
    ON parsing_error
    FOR EACH ROW
EXECUTE PROCEDURE set_created_at();

CREATE TRIGGER trg_parsing_error_set_updated_at
    BEFORE UPDATE
    ON parsing_error
    FOR EACH ROW
EXECUTE PROCEDURE set_updated_at();
