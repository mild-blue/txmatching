--
-- file: txmatching/database/db_migrations/0032.add-confirmation-columns-to-parsing-issue-model
-- depends: 0031.rename-parsing-errors-to-parsing-issues
--

ALTER TABLE parsing_issue ADD COLUMN confirmed_at TIMESTAMPTZ default NULL;
ALTER TABLE parsing_issue ADD COLUMN confirmed_by BIGINT default NULL;
ALTER TABLE parsing_issue
    ADD CONSTRAINT fk_parsing_issue_confirmed_by FOREIGN KEY (confirmed_by) REFERENCES app_user(id) ON DELETE SET NULL;
