--
-- file: txmatching/database/db_migrations/0011.add-user-to-allowed-event-table.sql
-- depends: 0010.add-patients-hash
--

CREATE TABLE user_to_allowed_event
(
    user_id      BIGINT      NOT NULL,
    txm_event_id BIGINT      NOT NULL,
    CONSTRAINT pk_user_to_allowed_event PRIMARY KEY (user_id, txm_event_id),
    CONSTRAINT fk_user_to_allowed_event_app_user_id FOREIGN KEY (user_id) REFERENCES app_user(id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_user_to_allowed_event_txm_event_id FOREIGN KEY (txm_event_id) REFERENCES txm_event(id) ON DELETE CASCADE ON UPDATE CASCADE
);
