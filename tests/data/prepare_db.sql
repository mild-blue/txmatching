TRUNCATE TABLE public.config RESTART IDENTITY CASCADE;
TRUNCATE TABLE public.app_user RESTART IDENTITY CASCADE;
TRUNCATE TABLE public.app_user RESTART IDENTITY CASCADE;
TRUNCATE TABLE public.pairing_result_patient RESTART IDENTITY CASCADE;

INSERT INTO public.app_user (email, pass_hash, role)
VALUES ('a', 'a', 'VIEWER');

INSERT INTO public.config (parameters, created_by)
VALUES ('{
  "enforce_same_blood_group": false
}', 1);

INSERT INTO public.config (parameters, created_by)
VALUES ('{
  "use_binary_scoring": true
}', 1);

INSERT INTO public.config (parameters, created_by)
VALUES ('{
  "use_binary_scoring": false
}', 1);

INSERT INTO public.pairing_result (config_id, calculated_matchings, score_matrix, valid)
VALUES (1, '[
  [
    {
      "recipient": 2,
      "donor": 1
    }
  ]
]', '{}', true);
INSERT INTO public.pairing_result (config_id, calculated_matchings, score_matrix, valid)
VALUES (2, '[
  [
    {
      "recipient": 2,
      "donor": 1
    }
  ]
]', '{}', true);


INSERT INTO public.pairing_result_patient (pairing_result_id, patient_id)
VALUES (1, 1);
INSERT INTO public.pairing_result_patient (pairing_result_id, patient_id)
VALUES (1, 2);
INSERT INTO public.pairing_result_patient (pairing_result_id, patient_id)
VALUES (2, 1);
INSERT INTO public.pairing_result_patient (pairing_result_id, patient_id)
VALUES (2, 2);
