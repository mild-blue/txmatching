--
-- file: txmatching/database/db_migrations/0018.add-txm-event-state.sql
-- depends: 0017.add-patient-note
--

CREATE TYPE TXM_EVENT_STATE AS ENUM (
    'OPEN',
    'CLOSED'
    );

ALTER TABLE txm_event
    ADD COLUMN state TXM_EVENT_STATE NOT NULL DEFAULT 'OPEN';
