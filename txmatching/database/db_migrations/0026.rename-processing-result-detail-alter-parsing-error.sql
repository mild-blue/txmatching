--
-- file: txmatching/database/db_migrations/0026.rename-processing-result-detail-alter-parsing-error.sql
-- depends: 0025.add-hla-code-processing-result-empty-group
--

ALTER TYPE HLA_CODE_PROCESSING_RESULT_DETAIL RENAME TO PARSING_ISSUE_DETAIL;
ALTER TABLE parsing_error RENAME COLUMN hla_code_processing_result_detail TO parsing_issue_detail;