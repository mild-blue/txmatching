TRUNCATE TABLE public.config RESTART IDENTITY CASCADE;

TRUNCATE TABLE public.app_user RESTART IDENTITY CASCADE;

TRUNCATE TABLE public.patient RESTART IDENTITY CASCADE;

INSERT INTO public.app_user (id, email, pass_hash, role, created_at, updated_at, deleted_at)
VALUES (1, 'a', 'a', 'VIEWER', '2020-07-09 19:24:31.284281', '2020-07-09 19:24:31.284281', null);

INSERT INTO public.config (id, parameters, created_by, created_at, updated_at, deleted_at)
VALUES (1, '{
  "enforce_same_blood_group": false
}', 1, '2020-07-09 19:24:44.823382', '2020-07-09 19:24:44.823382', null);

INSERT INTO public.config (id, parameters, created_by, created_at, updated_at, deleted_at)
VALUES (2, '{
  "use_binary_scoring": true
}', 1, '2020-07-09 19:24:44.823382', '2020-07-09 19:24:44.823382', null);

INSERT INTO public.config (id, parameters, created_by, created_at, updated_at, deleted_at)
VALUES (3, '{
  "use_binary_scoring": false
}', 1, '2020-07-09 19:24:44.823382', '2020-07-09 19:24:44.823382', null);


INSERT INTO public.patient (id, medical_id, country, patient_type, blood, typization, luminex, acceptable_blood, active,
                            created_at, updated_at, deleted_at)
VALUES (1, 'test', 'CZE', 'RECIPIENT', 'A', '{}', '{}', '{A}', true, '2020-07-09 21:56:54.312655',
        '2020-07-09 21:56:54.312655', null);
INSERT INTO public.patient (id, medical_id, country, patient_type, blood, typization, luminex, acceptable_blood, active,
                            created_at, updated_at, deleted_at)
VALUES (2, 'test2', 'CZE', 'DONOR', 'A', '{}', '{}', '{A}', true, '2020-07-09 21:56:54.312655',
        '2020-07-09 21:56:54.312655', null);

INSERT INTO public.pairing_result (id, config_id, calculated_matchings, score_matrix, valid, created_at, updated_at,
                                   deleted_at)
VALUES (1, 1, '[
  [
    {
      "recipient": 1,
      "donor": 2
    }
  ]
]', '{}', true, '2020-07-09 22:00:45.896175', '2020-07-09 22:00:45.896175', null);
INSERT INTO public.pairing_result (id, config_id, calculated_matchings, score_matrix, valid, created_at, updated_at,
                                   deleted_at)
VALUES (2, 2, '[
  [
    {
      "recipient": 1,
      "donor": 2
    }
  ]
]', '{}', true, '2020-07-09 22:01:04.182338', '2020-07-09 22:01:04.182338', null);


INSERT INTO public.pairing_result_patient (id, pairing_result_id, patient_id, created_at, updated_at, deleted_at)
VALUES (1, 1, 1, '2020-07-09 22:07:47.031941', '2020-07-09 22:07:47.031941', null);
INSERT INTO public.pairing_result_patient (id, pairing_result_id, patient_id, created_at, updated_at, deleted_at)
VALUES (2, 1, 2, '2020-07-09 22:07:47.031941', '2020-07-09 22:07:47.031941', null);
INSERT INTO public.pairing_result_patient (id, pairing_result_id, patient_id, created_at, updated_at, deleted_at)
VALUES (3, 2, 1, '2020-07-09 22:07:47.031941', '2020-07-09 22:07:47.031941', null);
INSERT INTO public.pairing_result_patient (id, pairing_result_id, patient_id, created_at, updated_at, deleted_at)
VALUES (4, 2, 2, '2020-07-09 22:07:47.031941', '2020-07-09 22:07:47.031941', null);


INSERT INTO public.patient_pair (id, recipient_id, donor_id, created_at, updated_at, deleted_at)
VALUES (1, 1, 2, '2020-07-09 23:01:23.746423', '2020-07-09 23:01:23.746423', null);
