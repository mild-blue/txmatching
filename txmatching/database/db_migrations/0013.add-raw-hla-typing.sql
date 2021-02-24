--
-- file: txmatching/database/db_migrations/0013.add-raw-hla-typing.sql
-- depends: 0012.add-user-to-allowed-event-table
--

ALTER TABLE donor
    ADD COLUMN hla_typing_raw JSONB NOT NULL;

ALTER TABLE recipient
    ADD COLUMN hla_typing_raw JSONB NOT NULL;

ALTER TABLE recipient
    ADD COLUMN hla_antibodies_raw JSONB NOT NULL;

ALTER TYPE HLA_CODE_PROCESSING_RESULT_DETAIL ADD VALUE 'MULTIPLE_CUTOFFS_PER_ANTIBODY';
