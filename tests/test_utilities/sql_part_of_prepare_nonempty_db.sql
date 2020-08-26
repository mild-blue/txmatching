TRUNCATE TABLE public.config RESTART IDENTITY CASCADE;
TRUNCATE TABLE public.pairing_result_patient RESTART IDENTITY CASCADE;

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
    ],
    "score": 1.0
  }]
}', '{"score_matrix_dto": [[1,2],[1,2]]}', true);
INSERT INTO public.pairing_result (config_id, calculated_matchings, score_matrix, valid)
VALUES (2, '{
  "matchings": [{
    "donors_recipients": [
      {
        "recipient": 3,
        "donor": 1
      }
    ],
    "score": 1.0
  }]
}', '{"score_matrix_dto": [[1,2],[1,2]]}', true);


INSERT INTO public.pairing_result_patient (pairing_result_id, patient_id)
VALUES (1, 1);
INSERT INTO public.pairing_result_patient (pairing_result_id, patient_id)
VALUES (1, 3);
INSERT INTO public.pairing_result_patient (pairing_result_id, patient_id)
VALUES (2, 1);
INSERT INTO public.pairing_result_patient (pairing_result_id, patient_id)
VALUES (2, 3);

