--
-- file: txmatching/database/db_migrations/0035.add-new-parsing-issue-detail.sql
-- depends: 0034.add-comp-graph-to-pairing-result
--

ALTER TYPE PARSING_ISSUE_DETAIL ADD VALUE 'HIGH_RES_WITH_ASSUMED_SPLIT_CODE';
