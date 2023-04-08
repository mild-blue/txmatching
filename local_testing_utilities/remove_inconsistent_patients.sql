/*
 Removes inconsistent patients.
 Most often, this is related to parsing_issue BASIC_HLA_GROUP_IS_EMPTY.
 */

DELETE FROM recipient
WHERE id IN
    (SELECT recipient.id FROM recipient
    JOIN parsing_issue ON parsing_issue.recipient_id=recipient.id
    WHERE parsing_issue.parsing_issue_detail = 'BASIC_HLA_GROUP_IS_EMPTY');

DELETE FROM donor
WHERE id IN
    (SELECT donor.id FROM donor
    JOIN parsing_issue ON parsing_issue.donor_id=donor.id
    WHERE parsing_issue.parsing_issue_detail = 'BASIC_HLA_GROUP_IS_EMPTY');
