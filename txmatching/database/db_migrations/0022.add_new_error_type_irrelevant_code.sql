--
-- file: txmatching/database/db_migrations/0022.add_new_error_type_irrelevant_code.sql
-- depends: 0021.add-missing-hla-code-processing-result
--

-- add new enum value for parsing error
ALTER TYPE HLA_CODE_PROCESSING_RESULT_DETAIL ADD VALUE 'IRRELEVANT_CODE';
