--
-- file: txmatching/database/db_migrations/0037.add-attribute-to-parsing-issue-detail.sql
-- depends: 0036.add-attribute-to-txm-event-base
--

ALTER TYPE PARSING_ISSUE_DETAIL ADD VALUE 'DUPLICATE_ANTIBODY_SINGLE_CHAIN';
ALTER TYPE PARSING_ISSUE_DETAIL ADD VALUE 'CREATED_THEORETICAL_ANTIBODY';
