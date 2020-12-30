--
-- file: txmatching/database/db_migrations/0007.add-uploaded-files-table.sql
-- depends: 0006.remove-active-column-from-recipient
--

CREATE TABLE uploaded_file
(
    id           BIGSERIAL   NOT NULL,
    file_name    TEXT        NOT NULL,
    file         BYTEA       NOT NULL,
    txm_event_id BIGINT      NOT NULL,
    user_id      BIGINT      NOT NULL,
    created_at   TIMESTAMPTZ NOT NULL,
    updated_at   TIMESTAMPTZ NOT NULL,
    deleted_at   TIMESTAMPTZ,
    CONSTRAINT pk_uploaded_file_id PRIMARY KEY (id),
    CONSTRAINT fk_uploaded_file_txm_event_id_txm_event_id FOREIGN KEY (txm_event_id) REFERENCES txm_event(id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_uploaded_file_user_id_app_user_id FOREIGN KEY (user_id) REFERENCES app_user(id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TRIGGER trg_uploaded_file_set_created_at
    BEFORE INSERT
    ON uploaded_file
    FOR EACH ROW
    EXECUTE PROCEDURE set_created_at();

CREATE TRIGGER trg_uploaded_file_set_updated_at
    BEFORE UPDATE
    ON uploaded_file
    FOR EACH ROW
    EXECUTE PROCEDURE set_updated_at();
