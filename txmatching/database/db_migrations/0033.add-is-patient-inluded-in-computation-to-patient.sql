--
-- file: txmatching/database/db_migrations/0033.add-is-patient-inluded-in-computation-to-patient
-- depends: 0032.add-confirmation-columns-to-parsing-issue-model
--

ALTER TABLE donor ADD COLUMN patient_has_confirmed_warnings BOOLEAN default NULL;
ALTER TABLE recipient ADD COLUMN patient_has_confirmed_warnings BOOLEAN default NULL;
