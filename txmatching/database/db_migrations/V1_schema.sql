CREATE TYPE USER_ROLE AS ENUM (
    'VIEWER',
    'EDITOR',
    'ADMIN',
    'SERVICE'
    );

CREATE TYPE DONOR_TYPE AS ENUM (
    'DONOR',
    'BRIDGING_DONOR',
    'NON_DIRECTED'
    );

CREATE TYPE COUNTRY AS ENUM (
    'CZE',
    'AUT',
    'IL'
    );

CREATE TYPE BLOOD_TYPE AS ENUM (
    'A',
    'B',
    'AB',
    '0'
    );

CREATE TYPE SEX AS ENUM (
    'F',
    'M'
    );

-- BEFORE insert function for trigger
CREATE OR REPLACE FUNCTION set_created_at() RETURNS TRIGGER
AS
$BODY$
BEGIN
    new.created_at := now();
    new.updated_at := new.created_at;
    RETURN new;
END;
$BODY$
    LANGUAGE plpgsql;

-- BEFORE update function for trigger
CREATE OR REPLACE FUNCTION set_updated_at() RETURNS TRIGGER
AS
$BODY$
BEGIN
    new.updated_at := now();
    RETURN new;
END;
$BODY$
    LANGUAGE plpgsql;


CREATE TABLE app_user
(
    id         BIGSERIAL   NOT NULL,
    email      TEXT        NOT NULL, -- serves as username
    pass_hash  TEXT        NOT NULL,
    role       USER_ROLE   NOT NULL,
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL,
    deleted_at TIMESTAMPTZ,
    CONSTRAINT pk_app_user_id PRIMARY KEY (id),
    CONSTRAINT uq_app_user_email UNIQUE (email)
);


CREATE TABLE txm_event
(
    id         BIGSERIAL   NOT NULL,
    name       TEXT        NOT NULL,
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL,
    deleted_at TIMESTAMPTZ,
    CONSTRAINT pk_txm_event_id PRIMARY KEY (id),
    CONSTRAINT uq_txm_event_name UNIQUE (name)
);

CREATE TABLE recipient
(
    id                     BIGSERIAL   NOT NULL,
    medical_id             TEXT        NOT NULL,
    txm_event_id           BIGINT      NOT NULL,
    country                COUNTRY     NOT NULL,
    blood                  BLOOD_TYPE  NOT NULL,
    hla_typing             JSONB       NOT NULL, -- JSON
    active                 BOOL        NOT NULL, -- assume some patients fall out of the set
    recipient_requirements JSONB       NOT NULL, -- JSON
    recipient_cutoff       INT         NOT NULL,
    sex                    SEX,
    height                 INT,
    weight                 NUMERIC,
    yob                    INT,
    waiting_since          timestamptz,
    previous_transplants   INT,
    created_at             TIMESTAMPTZ NOT NULL,
    updated_at             TIMESTAMPTZ NOT NULL,
    deleted_at             TIMESTAMPTZ,
    CONSTRAINT pk_recipient_id PRIMARY KEY (id),
    CONSTRAINT uq_recipient_medical_id UNIQUE (medical_id, txm_event_id),
    CONSTRAINT fk_recipient_txm_event_id_txm_event_id FOREIGN KEY (txm_event_id) REFERENCES txm_event (id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE donor
(
    id           BIGSERIAL   NOT NULL,
    medical_id   TEXT        NOT NULL,
    txm_event_id BIGINT      NOT NULL,
    recipient_id BIGINT,
    country      COUNTRY     NOT NULL,
    donor_type   DONOR_TYPE  NOT NULL,
    blood        BLOOD_TYPE  NOT NULL,
    hla_typing   JSONB       NOT NULL, -- JSON
    active       BOOL        NOT NULL, -- assume some patients fall out of the set
    sex          SEX,
    height       INT,
    weight       NUMERIC,
    yob          INT,
    created_at   TIMESTAMPTZ NOT NULL,
    updated_at   TIMESTAMPTZ NOT NULL,
    deleted_at   TIMESTAMPTZ,
    CONSTRAINT pk_donor_id PRIMARY KEY (id),
    CONSTRAINT uq_donor_medical_id UNIQUE (medical_id, txm_event_id),
    CONSTRAINT fk_donor_recipient_id_recipient_id FOREIGN KEY (recipient_id) REFERENCES recipient (id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_donor_txm_event_id_txm_event_id FOREIGN KEY (txm_event_id) REFERENCES txm_event (id) ON DELETE CASCADE ON UPDATE CASCADE


);

CREATE TABLE recipient_acceptable_blood
(
    id           BIGSERIAL   NOT NULL,
    recipient_id BIGINT      NOT NULL,
    blood_type   BLOOD_TYPE  NOT NULL,
    created_at   TIMESTAMPTZ NOT NULL,
    updated_at   TIMESTAMPTZ NOT NULL,
    deleted_at   TIMESTAMPTZ,
    CONSTRAINT pk_recipient_acceptable_blood_id PRIMARY KEY (id),
    CONSTRAINT fk_recipient_acceptable_blood_recipient_id_recipient_id FOREIGN KEY (recipient_id) REFERENCES recipient (id) ON DELETE CASCADE ON UPDATE CASCADE
);


CREATE TABLE recipient_hla_antibodies
(
    id           BIGSERIAL   NOT NULL,
    recipient_id BIGINT      NOT NULL,
    raw_code     TEXT        NOT NULL,
    mfi          INT         NOT NULL,
    cutoff       INT         NOT NULL,
    code         TEXT,
    created_at   TIMESTAMPTZ NOT NULL,
    updated_at   TIMESTAMPTZ NOT NULL,
    deleted_at   TIMESTAMPTZ,
    CONSTRAINT uq_recipient_hla_antibodies_code_recipient_id UNIQUE (raw_code, recipient_id),
    CONSTRAINT pk_recipient_hla_antibodies_id PRIMARY KEY (id),
    CONSTRAINT fk_recipient_hla_antibodies_recipient_id_recipient_id FOREIGN KEY (recipient_id) REFERENCES recipient (id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE config
(
    id           BIGSERIAL   NOT NULL,
    txm_event_id BIGINT      NOT NULL,
    parameters   JSONB       NOT NULL,                                                             -- JSON
    created_by   BIGINT      NOT NULL,
    created_at   TIMESTAMPTZ NOT NULL,
    updated_at   TIMESTAMPTZ NOT NULL,
    deleted_at   TIMESTAMPTZ,
    CONSTRAINT pk_config_id PRIMARY KEY (id),
    CONSTRAINT fk_config_created_by_app_user_id FOREIGN KEY (created_by) REFERENCES app_user (id), -- this is also valid for pairing_result
    CONSTRAINT fk_config_txm_event_id_txm_event_id FOREIGN KEY (txm_event_id) REFERENCES txm_event (id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE pairing_result
(
    id                   BIGSERIAL   NOT NULL,
    config_id            BIGINT      NOT NULL,
    calculated_matchings JSONB       NOT NULL, -- JSON
    score_matrix         JSONB       NOT NULL, -- matrix (list of lists) of computed compatibility indexes among patients (JSON)
    valid                BOOL        NOT NULL,
    created_at           TIMESTAMPTZ NOT NULL,
    updated_at           TIMESTAMPTZ NOT NULL,
    deleted_at           TIMESTAMPTZ,
    CONSTRAINT pk_pairing_result_id PRIMARY KEY (id),
    CONSTRAINT fk_pairing_result_config_id_config_id FOREIGN KEY (config_id) REFERENCES config (id) ON DELETE CASCADE ON UPDATE CASCADE
);


DO
$$
    DECLARE
        t TEXT;
    BEGIN
        FOR t IN
            SELECT table_name FROM information_schema.columns WHERE column_name = 'created_at'
            LOOP
                EXECUTE format('CREATE TRIGGER trg_%I_set_created_at
                    BEFORE INSERT ON %I
                    FOR EACH ROW EXECUTE PROCEDURE set_created_at()', t, t);
            END LOOP;
    END;
$$
LANGUAGE plpgsql;


DO
$$
    DECLARE
        t TEXT;
    BEGIN
        FOR t IN
            SELECT table_name FROM information_schema.columns WHERE column_name = 'updated_at'
            LOOP
                EXECUTE format('CREATE TRIGGER trg_%I_set_updated_at
                    BEFORE UPDATE ON %I
                    FOR EACH ROW EXECUTE PROCEDURE set_updated_at()', t, t);
            END LOOP;
    END;
$$
LANGUAGE plpgsql;

-- TODO add indexes (probably only when actually needed)
--  (https://trello.com/c/H1gtKSao/89-add-indexes-to-db-probably-only-when-actually-needed)
-- TODO add (before|instead) triggers for delete (https://trello.com/c/MfPrpOp1/90-add-beforeinstead-triggers-for-delete-to-db)
