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

CREATE TABLE role (
    id        BIGSERIAL NOT NULL,
    user_role USER_ROLE NOT NULL,
    CONSTRAINT pkey_role_id PRIMARY KEY (id)
);

INSERT INTO role (user_role)
VALUES ('VIEWER'),
    ('EDITOR'),
    ('ADMIN');

CREATE TABLE app_user (
    id        BIGSERIAL   NOT NULL,
    email     VARCHAR     NOT NULL, -- serves as username
    pass_hash VARCHAR     NOT NULL,
    created   TIMESTAMPTZ NOT NULL,
    updated   TIMESTAMPTZ NOT NULL,
    deleted   TIMESTAMPTZ,
    CONSTRAINT pkey_app_user_id PRIMARY KEY (id),
    CONSTRAINT uq_app_user_email UNIQUE (email)
);

CREATE TABLE app_user_role (
    app_user_id BIGINT      NOT NULL,
    role_id     BIGINT      NOT NULL,
    created     TIMESTAMPTZ NOT NULL,
    updated     TIMESTAMPTZ NOT NULL,
    deleted     TIMESTAMPTZ,
    CONSTRAINT pkey_app_user_role PRIMARY KEY (app_user_id, role_id),
    CONSTRAINT uq_app_user_role UNIQUE (app_user_id, role_id),
    CONSTRAINT fkey_app_user_role FOREIGN KEY (role_id) REFERENCES role(id) ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT fkey_app_user_app_user FOREIGN KEY (app_user_id) REFERENCES app_user(id) ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE patient (
    id               BIGSERIAL    NOT NULL,
    medical_id       VARCHAR      NOT NULL,
    country          COUNTRY      NOT NULL,
    patient_type     PATIENT_TYPE NOT NULL,
    blood            BLOOD_TYPE   NOT NULL,
    acceptable_blood VARCHAR      NOT NULL, -- list of BLOOD_TYPE
    typization       JSONB        NOT NULL, -- JSON
    luminex          JSONB        NOT NULL, -- JSON
    active           BOOLEAN      NOT NULL, -- assume some patients fall out of the set
    created          TIMESTAMPTZ  NOT NULL,
    updated          TIMESTAMPTZ  NOT NULL,
    deleted          TIMESTAMPTZ,
    CONSTRAINT pkey_patient_id PRIMARY KEY (id)
);

CREATE TABLE patient_pair (
    id           BIGSERIAL   NOT NULL,
    recipient_id BIGINT      NOT NULL,
    donor_id     BIGINT      NOT NULL,
    created      TIMESTAMPTZ NOT NULL,
    updated      TIMESTAMPTZ NOT NULL,
    deleted      TIMESTAMPTZ,
    CONSTRAINT pkey_patient_pair_id PRIMARY KEY (id),
    CONSTRAINT fkey_patient_pair_recipient_id_patient_id FOREIGN KEY (recipient_id) REFERENCES patient(id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fkey_patient_pair_donor_id_patient_id FOREIGN KEY (donor_id) REFERENCES patient(id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT uq_patient_pair_recipient_id_donor_id UNIQUE (recipient_id, donor_id)
);

CREATE TABLE config (
    id         BIGSERIAL   NOT NULL,
    parameters JSONB       NOT NULL,                                                               -- structured JSON
    created_by BIGINT      NOT NULL,
    created    TIMESTAMPTZ NOT NULL,
    updated    TIMESTAMPTZ NOT NULL,
    deleted    TIMESTAMPTZ,
    CONSTRAINT pkey_config_id PRIMARY KEY (id),
    CONSTRAINT uq_config_parameters UNIQUE (parameters),
    CONSTRAINT fkey_config_created_by_app_user_id FOREIGN KEY (created_by) REFERENCES app_user(id) -- this is also valid for pairing_result
);

CREATE TABLE pairing_result (
    id                   BIGSERIAL   NOT NULL,
    config_id            BIGINT      NOT NULL,
    patient_ids          JSONB       NOT NULL, -- list of patient_id (or JSON)
    calculated_matchings JSONB       NOT NULL, -- JSON
    score_matrix         VARCHAR     NOT NULL, -- matrix (list of lists) of computed compatibility indexes among patients
    valid                BOOLEAN     NOT NULL,
    created              TIMESTAMPTZ NOT NULL,
    updated              TIMESTAMPTZ NOT NULL,
    deleted              TIMESTAMPTZ,
    CONSTRAINT pkey_pairing_result_id PRIMARY KEY (id),
    CONSTRAINT fkey_pairing_result_config_id_config_id FOREIGN KEY (config_id) REFERENCES config(id) ON DELETE CASCADE ON UPDATE CASCADE
);

-- TODO add indexes (probably only when actually needed)
-- TODO add before triggers for auditing