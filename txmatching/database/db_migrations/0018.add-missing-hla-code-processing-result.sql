--
-- file: txmatching/database/db_migrations/0018.add-missing-hla-code-processing-result.sql
-- depends: 0017.add-patient-note
--

ALTER TYPE HLA_CODE_PROCESSING_RESULT_DETAIL ADD VALUE 'HIGH_RES_WITH_LETTER';
