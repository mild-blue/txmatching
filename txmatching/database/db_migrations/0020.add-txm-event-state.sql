--
-- file: txmatching/database/db_migrations/0020.add-txm-event-state.sql
-- depends: 0019.add-and-remove-missing-hla-code-processing-result
--

CREATE TYPE TXM_EVENT_STATE AS ENUM (
    'OPEN',
    'CLOSED'
    );

ALTER TABLE txm_event
    ADD COLUMN state TXM_EVENT_STATE NOT NULL DEFAULT 'OPEN';
