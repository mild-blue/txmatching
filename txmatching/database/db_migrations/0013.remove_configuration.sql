--
-- file: txmatching/database/db_migrations/0013.remove_configuration.sql
-- depends: 0012.add-patients-hash
--

TRUNCATE TABLE config CASCADE;
