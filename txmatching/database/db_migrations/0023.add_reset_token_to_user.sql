--
-- file: txmatching/database/db_migrations/0023.add_reset_token_to_user.sql
-- depends: 0022.add_new_error_type_irrelevant_code
--

ALTER TABLE app_user
    ADD COLUMN reset_token TEXT default NULL
