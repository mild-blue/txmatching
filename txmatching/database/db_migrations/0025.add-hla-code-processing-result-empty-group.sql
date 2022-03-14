--
-- file: txmatching/database/db_migrations/0025.add-hla-code-processing-result-empty-group.sql
-- depends: 0024.drop_constraint_config
--

ALTER TYPE HLA_CODE_PROCESSING_RESULT_DETAIL ADD VALUE 'BASIC_HLA_GROUP_IS_EMPTY';
