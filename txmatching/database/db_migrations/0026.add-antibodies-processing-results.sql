--
-- file: txmatching/database/db_migrations/0026.add-antibodies-processing-result.sql
-- depends: 0025.add-hla-code-processing-result-empty-group
--

ALTER TYPE HLA_CODE_PROCESSING_RESULT_DETAIL ADD VALUE 'INSUFFICIENT_NUMBER_OF_ANTIBODIES_IN_HIGH_RES';
ALTER TYPE HLA_CODE_PROCESSING_RESULT_DETAIL ADD VALUE 'ALL_ANTIBODIES_ARE_POSITIVE_IN_HIGH_RES';
