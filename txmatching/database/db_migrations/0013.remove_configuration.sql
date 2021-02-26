--
-- file: txmatching/database/db_migrations/0013.remove_configuration.sql
-- depends: 0012.add-user-to-allowed-event-table
--

TRUNCATE TABLE config CASCADE;
