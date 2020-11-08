--
-- file: 0006.remove-active-column-from-recipient.sql
-- depends: 0005.add-unique-configuration-for-txm-event
--

ALTER TABLE recipient
    DROP COLUMN active
