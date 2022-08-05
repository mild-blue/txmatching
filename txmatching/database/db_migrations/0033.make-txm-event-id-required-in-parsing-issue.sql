--
-- file: txmatching/database/db_migrations/0033.make-txm-event-id-required-in-parsing-issue.sql
-- depends: 0032.add-confirmation-columns-to-parsing-issue-model
--

ALTER TABLE parsing_issue ALTER COLUMN txm_event_id SET NOT NULL;
ALTER TABLE parsing_issue ALTER COLUMN hla_code_or_group SET NOT NULL;
ALTER TABLE parsing_issue ADD CHECK ((donor_id IS NOT NULL) OR (recipient_id IS NOT NULL));
