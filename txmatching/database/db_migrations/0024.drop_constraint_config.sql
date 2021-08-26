--
-- file: txmatching/database/db_migrations/0024.drop_constraint_config.sql
-- depends: 0023.add_reset_token_to_user
--

ALTER TABLE pairing_result
    DROP CONSTRAINT uq_pairing_result_config_id;
