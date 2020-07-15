TRUNCATE TABLE public.config RESTART IDENTITY CASCADE;
TRUNCATE TABLE public.app_user RESTART IDENTITY CASCADE;
TRUNCATE TABLE public.app_user RESTART IDENTITY CASCADE;
TRUNCATE TABLE public.pairing_result_patient RESTART IDENTITY CASCADE;

-- Test user with password "aaa"
INSERT INTO public.app_user (id, email, pass_hash, role)
VALUES (1, 'admin@example.com', '$2b$12$3A5.4Ulau0F6AUksx9bojuYygMGNjdyPqHzrCJ1ELjqbcV28YU1Rq', 'ADMIN');


INSERT INTO public.config (parameters, created_by)
VALUES ('{
  "enforce_compatible_blood_group": false
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
VALUES (1, '{
  "matchings": [{
    "donors_recipients": [
      {
        "recipient": 3,
        "donor": 1
      }
    ]
  }]
}', '{}', true);
INSERT INTO public.pairing_result (config_id, calculated_matchings, score_matrix, valid)
VALUES (2, '{
  "matchings": [{
    "donors_recipients": [
      {
        "recipient": 3,
        "donor": 1
      }
    ]
  }]
}', '{}', true);


INSERT INTO public.pairing_result_patient (pairing_result_id, patient_id)
VALUES (1, 1);
INSERT INTO public.pairing_result_patient (pairing_result_id, patient_id)
VALUES (1, 3);
INSERT INTO public.pairing_result_patient (pairing_result_id, patient_id)
VALUES (2, 1);
INSERT INTO public.pairing_result_patient (pairing_result_id, patient_id)
VALUES (2, 3);

