--
-- file: txmatching/database/db_migrations/0006.remove-active-column-from-recipient.sql
-- depends: 0005.add-country-to-user.sql
--

ALTER TABLE recipient
    DROP COLUMN active
