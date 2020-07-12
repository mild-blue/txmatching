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


CREATE TABLE patient
(
    id             BIGSERIAL    NOT NULL,
    medical_id     TEXT         NOT NULL,
    country        COUNTRY      NOT NULL,
    patient_type   PATIENT_TYPE NOT NULL,
    blood          BLOOD_TYPE   NOT NULL,
    hla_antigens   JSONB        NOT NULL, -- JSON
    hla_antibodies JSONB        NOT NULL, -- JSON
    active         BOOL         NOT NULL, -- assume some patients fall out of the set
    created_at     TIMESTAMPTZ  NOT NULL,
    updated_at     TIMESTAMPTZ  NOT NULL,
    deleted_at     TIMESTAMPTZ,
    CONSTRAINT pk_patient_id PRIMARY KEY (id),
    CONSTRAINT uq_medical_id UNIQUE (medical_id)
);

CREATE TABLE patient_acceptable_blood
(
    id         BIGSERIAL   NOT NULL,
    patient_id BIGINT      NOT NULL,
    blood_type BLOOD_TYPE  NOT NULL,
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL,
    deleted_at TIMESTAMPTZ,
    CONSTRAINT pk_patient_acceptable_blood_id PRIMARY KEY (id),
    CONSTRAINT fk_patient_acceptable_blood_patient_id_patient_id FOREIGN KEY (patient_id) REFERENCES patient (id) ON DELETE CASCADE ON UPDATE CASCADE
);



CREATE TABLE patient_pair
(
    id           BIGSERIAL   NOT NULL,
    recipient_id BIGINT      NOT NULL,
    donor_id     BIGINT      NOT NULL,
    created_at   TIMESTAMPTZ NOT NULL,
    updated_at   TIMESTAMPTZ NOT NULL,
    deleted_at   TIMESTAMPTZ,
    CONSTRAINT pk_patient_pair_id PRIMARY KEY (id),
    CONSTRAINT fk_patient_pair_recipient_id_patient_id FOREIGN KEY (recipient_id) REFERENCES patient (id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_patient_pair_donor_id_patient_id FOREIGN KEY (donor_id) REFERENCES patient (id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT uq_patient_pair_recipient_id_donor_id UNIQUE (recipient_id, donor_id)
);

CREATE TABLE config
(
    id         BIGSERIAL   NOT NULL,
    parameters JSONB       NOT NULL,                                                              -- JSON
    created_by BIGINT      NOT NULL,
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL,
    deleted_at TIMESTAMPTZ,
    CONSTRAINT pk_config_id PRIMARY KEY (id),
    CONSTRAINT fk_config_created_by_app_user_id FOREIGN KEY (created_by) REFERENCES app_user (id) -- this is also valid for pairing_result
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

CREATE TABLE pairing_result_patient
(
    id                BIGSERIAL   NOT NULL,
    pairing_result_id BIGINT      NOT NULL,
    patient_id        BIGINT      NOT NULL,
    created_at        TIMESTAMPTZ NOT NULL,
    updated_at        TIMESTAMPTZ NOT NULL,
    deleted_at        TIMESTAMPTZ,
    CONSTRAINT pk_pairing_result_patient_id PRIMARY KEY (id),
    CONSTRAINT fk_pairing_result_patient_pairing_result_id FOREIGN KEY (pairing_result_id) REFERENCES pairing_result (id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_pairing_result_patient_patient_id FOREIGN KEY (patient_id) REFERENCES patient (id) ON DELETE CASCADE ON UPDATE CASCADE
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

-- TODO add indexes (probably only when actually needed) (https://trello.com/c/H1gtKSao/89-add-indexes-to-db-probably-only-when-actually-needed)
-- TODO add (before|instead) triggers for delete (https://trello.com/c/MfPrpOp1/90-add-beforeinstead-triggers-for-delete-to-db)
