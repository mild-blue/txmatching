CREATE TYPE USER_ROLE AS ENUM (
    'VIEWER',
    'EDITOR',
    'ADMIN'
    );

CREATE TYPE PATIENT_TYPE AS ENUM (
    'RECIPIENT',
    'DONOR',
    'BRIDGING_DONOR',
    'ALTRUIST'
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


CREATE TABLE role (
    id        BIGSERIAL NOT NULL,
    user_role USER_ROLE NOT NULL,
    CONSTRAINT pkey_role_id PRIMARY KEY (id)
);

INSERT INTO role (user_role)
VALUES ('VIEWER'),
    ('EDITOR'),
    ('ADMIN');

CREATE TABLE blood (
    id         BIGSERIAL  NOT NULL,
    blood_type BLOOD_TYPE NOT NULL,
    CONSTRAINT pkey_blood_id PRIMARY KEY (id)
);

INSERT INTO blood (blood_type)
VALUES ('A'),
    ('B'),
    ('AB'),
    ('0');

CREATE TABLE app_user (
    id         BIGSERIAL   NOT NULL,
    email      TEXT        NOT NULL, -- serves as username
    pass_hash  TEXT        NOT NULL,
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL,
    deleted_at TIMESTAMPTZ,
    CONSTRAINT pkey_app_user_id PRIMARY KEY (id),
    CONSTRAINT uq_app_user_email UNIQUE (email)
);

CREATE TABLE app_user_role (
    app_user_id BIGINT      NOT NULL,
    role_id     BIGINT      NOT NULL,
    created_at  TIMESTAMPTZ NOT NULL,
    updated_at  TIMESTAMPTZ NOT NULL,
    deleted_at  TIMESTAMPTZ,
    CONSTRAINT pkey_app_user_role PRIMARY KEY (app_user_id, role_id),
    CONSTRAINT uq_app_user_role UNIQUE (app_user_id, role_id),
    CONSTRAINT fkey_app_user_role FOREIGN KEY (role_id) REFERENCES role(id) ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT fkey_app_user_app_user FOREIGN KEY (app_user_id) REFERENCES app_user(id) ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE patient (
    id           BIGSERIAL    NOT NULL,
    medical_id   TEXT         NOT NULL,
    country      COUNTRY      NOT NULL,
    patient_type PATIENT_TYPE NOT NULL,
    blood        BLOOD_TYPE   NOT NULL,
    typization   JSONB        NOT NULL, -- JSON
    luminex      JSONB        NOT NULL, -- JSON
    active       BOOLEAN      NOT NULL, -- assume some patients fall out of the set
    created_at   TIMESTAMPTZ  NOT NULL,
    updated_at   TIMESTAMPTZ  NOT NULL,
    deleted_at   TIMESTAMPTZ,
    CONSTRAINT pkey_patient_id PRIMARY KEY (id)
);

CREATE TABLE patient_acceptable_blood (
    id         BIGSERIAL   NOT NULL,
    patient_id BIGINT      NOT NULL,
    blood_id   BIGINT      NOT NULL,
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL,
    deleted_at TIMESTAMPTZ,
    CONSTRAINT pkey_patient_acceptable_blood_id PRIMARY KEY (id),
    CONSTRAINT uq_patient_acceptable_blood_patient_id_blood_id UNIQUE (patient_id, blood_id),
    CONSTRAINT fkey_patient_acceptable_blood_patient_id FOREIGN KEY (patient_id) REFERENCES patient(id) ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT fkey_patient_acceptable_blood_blood_id FOREIGN KEY (blood_id) REFERENCES blood(id) ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE patient_pair (
    id           BIGSERIAL   NOT NULL,
    recipient_id BIGINT      NOT NULL,
    donor_id     BIGINT      NOT NULL,
    created_at   TIMESTAMPTZ NOT NULL,
    updated_at   TIMESTAMPTZ NOT NULL,
    deleted_at   TIMESTAMPTZ,
    CONSTRAINT pkey_patient_pair_id PRIMARY KEY (id),
    CONSTRAINT fkey_patient_pair_recipient_id_patient_id FOREIGN KEY (recipient_id) REFERENCES patient(id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fkey_patient_pair_donor_id_patient_id FOREIGN KEY (donor_id) REFERENCES patient(id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT uq_patient_pair_recipient_id_donor_id UNIQUE (recipient_id, donor_id)
);

CREATE TABLE config (
    id            BIGSERIAL   NOT NULL,
    parameters    JSONB       NOT NULL,                                                                  -- JSON
    created_at_by BIGINT      NOT NULL,
    created_at    TIMESTAMPTZ NOT NULL,
    updated_at    TIMESTAMPTZ NOT NULL,
    deleted_at    TIMESTAMPTZ,
    CONSTRAINT pkey_config_id PRIMARY KEY (id),
    CONSTRAINT uq_config_parameters UNIQUE (parameters),
    CONSTRAINT fkey_config_created_at_by_app_user_id FOREIGN KEY (created_at_by) REFERENCES app_user(id) -- this is also valid for pairing_result
);

CREATE TABLE pairing_result (
    id                   BIGSERIAL   NOT NULL,
    config_id            BIGINT      NOT NULL,
    patient_ids          JSONB       NOT NULL, -- list of patient_id (JSON)
    calculated_matchings JSONB       NOT NULL, -- JSON
    score_matrix         JSONB       NOT NULL, -- matrix (list of lists) of computed compatibility indexes among patients (JSON)
    valid                BOOLEAN     NOT NULL,
    created_at           TIMESTAMPTZ NOT NULL,
    updated_at           TIMESTAMPTZ NOT NULL,
    deleted_at           TIMESTAMPTZ,
    CONSTRAINT pkey_pairing_result_id PRIMARY KEY (id),
    CONSTRAINT fkey_pairing_result_config_id_config_id FOREIGN KEY (config_id) REFERENCES config(id) ON DELETE CASCADE ON UPDATE CASCADE
);

DO
$$
    DECLARE
        t TEXT;
    BEGIN
        FOR t IN
            SELECT table_name FROM information_schema.columns WHERE column_name = 'created_at'
            LOOP
                EXECUTE format('CREATE TRIGGER trigger_set_created_at
                    BEFORE UPDATE ON %I
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
                EXECUTE format('CREATE TRIGGER trigger_set_updated_at
                    BEFORE UPDATE ON %I
                    FOR EACH ROW EXECUTE PROCEDURE set_updated_at()', t, t);
            END LOOP;
    END;
$$
LANGUAGE plpgsql;

-- TODO add indexes (probably only when actually needed)
-- TODO add (before|instead) triggers for delete