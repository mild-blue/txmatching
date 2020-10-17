--
-- file: 0003.add-country-to-user.sql
-- depends: 0001.initial-schema.sql
--

ALTER TABLE public.app_user
    -- with '_' as prefix in order to indicate private field in the python
    ADD COLUMN _allowed_edit_countries TEXT NOT NULL DEFAULT '';
