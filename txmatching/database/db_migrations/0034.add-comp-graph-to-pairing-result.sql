--
-- file: txmatching/database/db_migrations/0034.add-comp-graph-to-pairing-result.sql
-- depends: 0033.make-txm-event-id-required-in-parsing-issue
--

ALTER TABLE pairing_result DROP COLUMN score_matrix;
ALTER TABLE pairing_result ADD COLUMN compatibility_graph JSONB NOT NULL;
