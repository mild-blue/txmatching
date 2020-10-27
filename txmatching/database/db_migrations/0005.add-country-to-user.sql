--
-- file: 0005.add-country-to-user.sql
-- depends: 0004.add-unique-configuration-for-txm-event
--

-- with '_' as prefix in order to indicate private field in Python
ALTER TABLE app_user
    ADD COLUMN allowed_edit_countries jsonb not null default '[]'::jsonb
