--
-- file: txmatching/database/db_migrations/0014.add_new_error_type.sql
-- depends: 0013.remove_configuration
--

-- add new enum value for parsing error
ALTER TYPE HLA_CODE_PROCESSING_RESULT_DETAIL ADD VALUE 'HIGH_RES_WITHOUT_SPLIT';
