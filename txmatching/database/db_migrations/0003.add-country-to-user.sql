--
-- file: 0003.add-country-to-user.sql
-- depends: 0002.drop-unique-recipient-antibodies
--

-- with '_' as prefix in order to indicate private field in the python
ALTER TABLE app_user
    ADD COLUMN _allowed_edit_countries TEXT NOT NULL DEFAULT '';
