--
-- file: 0005.add-country-to-user.sql
-- depends: 0004.add-unique-configuration-for-txm-event
--

ALTER TABLE app_user
    ADD COLUMN allowed_edit_countries jsonb not null default '[]'::jsonb
