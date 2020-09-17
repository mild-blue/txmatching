TRUNCATE TABLE public.config RESTART IDENTITY CASCADE;
TRUNCATE TABLE public.pairing_result RESTART IDENTITY CASCADE;

INSERT INTO public.txm_event (name)
VALUES ('initial_session');

INSERT INTO public.config (parameters, created_by, txm_event_id)
VALUES ('{
  "enforce_compatible_blood_group": false
}', 1, 1);

INSERT INTO public.config (parameters, created_by, txm_event_id)
VALUES ('{
  "use_binary_scoring": true
}', 1, 1);

INSERT INTO public.config (parameters, created_by, txm_event_id)
VALUES ('{
  "use_binary_scoring": false
}', 1, 1);

INSERT INTO public.pairing_result (config_id, calculated_matchings, score_matrix, valid)
VALUES (1, '{
  "matchings": [{
    "donors_recipients": [
      {
        "recipient": 2,
        "donor": 1
      }
    ],
    "score": 1.0,
    "db_id": 1
  }]
}', '{"score_matrix_dto": [[1,2],[1,2]]}', true);
INSERT INTO public.pairing_result (config_id, calculated_matchings, score_matrix, valid)
VALUES (2, '{
  "matchings": [{
    "donors_recipients": [
      {
        "recipient": 2,
        "donor": 1
      }
    ],
    "score": 1.0,
    "db_id": 3
  }]
}', '{"score_matrix_dto": [[1,2],[1,2]]}', true);
