--
-- file: txmatching/database/db_migrations/0021.add-missing-hla-code-processing-result.sql
-- depends: 0020.add-txm-event-state
--

ALTER TYPE HLA_CODE_PROCESSING_RESULT_DETAIL ADD VALUE 'MORE_THAN_TWO_HLA_CODES_PER_GROUP';
