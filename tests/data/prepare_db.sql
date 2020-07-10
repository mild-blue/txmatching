TRUNCATE TABLE public.config RESTART IDENTITY CASCADE;
TRUNCATE TABLE public.app_user RESTART IDENTITY CASCADE;
TRUNCATE TABLE public.patient RESTART IDENTITY CASCADE;
TRUNCATE TABLE public.app_user RESTART IDENTITY CASCADE;
TRUNCATE TABLE public.pairing_result_patient RESTART IDENTITY CASCADE;
TRUNCATE TABLE public.patient_pair RESTART IDENTITY CASCADE;

INSERT INTO public.app_user (id, email, pass_hash, role)
VALUES (1, 'a', 'a', 'VIEWER');

INSERT INTO public.config (id, parameters, created_by)
VALUES (1, '{
  "enforce_same_blood_group": false
}', 1);

INSERT INTO public.config (id, parameters, created_by)
VALUES (2, '{
  "use_binary_scoring": true
}', 1);

INSERT INTO public.config (id, parameters, created_by)
VALUES (3, '{
  "use_binary_scoring": false
}', 1);


INSERT INTO public.patient (id, medical_id, country, patient_type, blood, typization, luminex, acceptable_blood, active)
VALUES (1, 'test', 'CZE', 'RECIPIENT', 'A', '{}', '{}', '{A}', true);
INSERT INTO public.patient (id, medical_id, country, patient_type, blood, typization, luminex, acceptable_blood, active)
VALUES (2, 'test2', 'CZE', 'DONOR', 'A', '{}', '{}', '{A}', true);

INSERT INTO public.pairing_result (id, config_id, calculated_matchings, score_matrix, valid)
VALUES (1, 1, '[
  [
    {
      "recipient": 1,
      "donor": 2
    }
  ]
]', '{}', true);
INSERT INTO public.pairing_result (id, config_id, calculated_matchings, score_matrix, valid)
VALUES (2, 2, '[
  [
    {
      "recipient": 1,
      "donor": 2
    }
  ]
]', '{}', true);


INSERT INTO public.pairing_result_patient (id, pairing_result_id, patient_id)
VALUES (1, 1, 1);
INSERT INTO public.pairing_result_patient (id, pairing_result_id, patient_id)
VALUES (2, 1, 2);
INSERT INTO public.pairing_result_patient (id, pairing_result_id, patient_id)
VALUES (3, 2, 1);
INSERT INTO public.pairing_result_patient (id, pairing_result_id, patient_id)
VALUES (4, 2, 2);


INSERT INTO public.patient_pair (id, recipient_id, donor_id)
VALUES (1, 1, 2);
