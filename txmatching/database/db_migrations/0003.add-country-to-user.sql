--
-- file: 0003.add-country-to-user.sql
-- depends: 0001.initial-schema.sql
--

ALTER TABLE public.app_user
    ADD COLUMN can_edit_countries COUNTRY[] NOT NULL DEFAULT [];
