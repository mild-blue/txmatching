--
-- file: txmatching/database/db_migrations/0038.add-warning-in-case-of-rare-hla.sql
-- depends: 0037.add-attribute-to-parsing-issue-detail
--

ALTER TYPE PARSING_ISSUE_DETAIL ADD VALUE 'RARE_ALLELE_POSITIVE_CROSSMATCH';
