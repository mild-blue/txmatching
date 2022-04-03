--
-- file: txmatching/database/db_migrations/0028.drop-medical-id-add-patient-db-id-in-parsing-error
-- depends: 0027.rename-processing-result-detail-alter-parsing-error
--
TRUNCATE TABLE parsing_error RESTART IDENTITY;
ALTER TABLE parsing_error DROP COLUMN medical_id;
ALTER TABLE parsing_error ADD COLUMN donor_id BIGINT default NULL;
ALTER TABLE parsing_error ADD COLUMN recipient_id BIGINT default NULL;
ALTER TABLE parsing_error
    ADD CONSTRAINT fk_parsing_error_donor_id FOREIGN KEY (donor_id) REFERENCES donor(id) ON DELETE CASCADE;
ALTER TABLE parsing_error
    ADD CONSTRAINT fk_parsing_error_recipient_id FOREIGN KEY (recipient_id) REFERENCES recipient(id) ON DELETE CASCADE;
