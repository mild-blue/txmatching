--
-- file: txmatching/database/0019.add-missing-hla-code-processing-result.sql
-- depends: 0018.add-missing-hla-code-processing-result
--

ALTER TYPE HLA_CODE_PROCESSING_RESULT_DETAIL ADD VALUE 'MULTIPLE_SPLITS_OR_BROADS_FOUND';
ALTER TYPE HLA_CODE_PROCESSING_RESULT_DETAIL ADD VALUE 'UNKNOWN_TRANSFORMATION_FROM_HIGH_RES';
