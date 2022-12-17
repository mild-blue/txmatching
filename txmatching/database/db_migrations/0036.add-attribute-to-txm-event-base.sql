--
-- file: txmatching/database/db_migrations/0036.add-attribute-to-txm-event-base.sql
-- depends: 0035.add-new-parsing-issue-detail
--

CREATE TYPE STRICTNESS_TYPE AS ENUM (
    'STRICT',
    'FORGIVING'
    );

ALTER TABLE txm_event ADD COLUMN strictness_type STRICTNESS_TYPE NOT NULL default 'STRICT';
ALTER TYPE PARSING_ISSUE_DETAIL ADD VALUE 'FORGIVING_HLA_PARSING';
