--
-- file: txmatching/database/db_migrations/0037.make-medical-id-unique.sql
-- depends: 0036.add-attribute-to-txm-event-base


-- patient must not have medical_id as donor already present in db within the same txm_event_id

CREATE FUNCTION check_medical_id()
    RETURNS TRIGGER AS $$
BEGIN
  IF
EXISTS (SELECT * FROM recipient WHERE medical_id = NEW.medical_id AND txm_event_id = NEW.txm_event_id) OR
     EXISTS (SELECT * FROM donor WHERE medical_id = NEW.medical_id AND txm_event_id = NEW.txm_event_id) THEN
    RAISE EXCEPTION 'Medical_id % is not unique in txm_event with id %', NEW.medical_id, NEW.txm_event_id;
END IF;
RETURN NEW;
END;
$$
LANGUAGE plpgsql;

CREATE TRIGGER check_recipient_medical_id
    BEFORE INSERT
    ON recipient
    FOR EACH ROW
    EXECUTE FUNCTION check_medical_id();

CREATE TRIGGER check_donor_medical_id
    BEFORE INSERT
    ON donor
    FOR EACH ROW
    EXECUTE FUNCTION check_medical_id();
