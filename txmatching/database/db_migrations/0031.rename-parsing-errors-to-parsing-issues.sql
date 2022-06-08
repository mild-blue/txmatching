--
-- file: txmatching/database/db_migrations/0031.rename-parsing-errors-to-parsing-issues.sql
-- depends: 0030.add-etag-to-patient-models
--

ALTER TABLE parsing_error RENAME TO parsing_issue;
