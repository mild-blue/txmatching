--
-- file: txmatching/database/db_migrations/0033.make-txm-event-id-required-in-parsing-issue.sql
-- depends: 0032.add-confirmation-columns-to-parsing-issue-model
--

ALTER TABLE parsing_issue ALTER column txm_event_id SET NOT NULL;