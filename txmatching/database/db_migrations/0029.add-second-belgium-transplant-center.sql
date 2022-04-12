--
-- file: txmatching/database/db_migrations/0029.add-second-belgium-transplant-center
-- depends: 0028.drop-medical-id-add-patient-db-id-in-parsing-error
--
ALTER TYPE COUNTRY ADD VALUE 'BEL_2';
