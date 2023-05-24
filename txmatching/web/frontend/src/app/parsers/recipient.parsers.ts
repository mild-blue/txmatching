import { RecipientGenerated, RecipientRequirementsGenerated, UpdatedRecipientGenerated } from "../generated";
import { Recipient, RecipientRequirements, UpdatedRecipient } from "../model";
import { parseBloodGroup, parsePatient, parseAllMessages } from "./patient.parsers";
import { parseAntibodies } from "./hla.parsers";
import { ListItem } from "@app/components/list-item/list-item.interface";
import { PatientPairItemComponent } from "@app/components/patient-pair-item/patient-pair-item.component";
import { PatientPairDetailComponent } from "@app/components/patient-pair-detail/patient-pair-detail.component";
import { parseParsingIssuePublic } from "./parsingIssuePublic.parsers";

export const parseRecipient = (data: RecipientGenerated): Recipient => {
  const recipientListItem: ListItem = {
    index: 0,
    isActive: false,
    itemComponent: PatientPairItemComponent,
    detailComponent: PatientPairDetailComponent,
  };

  return {
    ...parsePatient(data, recipientListItem),
    acceptableBloodGroups: data.acceptable_blood_groups?.map(parseBloodGroup) ?? [],
    hlaAntibodies: parseAntibodies(data.hla_antibodies),
    cutoff: data.recipient_cutoff,
    waitingSince: data.waiting_since ? parseDate(data.waiting_since) : undefined,
    // TODO: https://github.com/mild-blue/txmatching/issues/628
    //  we expect undefined from BE but we sometimes get null instead
    previousTransplants: data.previous_transplants !== null ? data.previous_transplants : undefined,
    recipientRequirements: data.recipient_requirements && parseRecipientRequirements(data.recipient_requirements),
    relatedDonorDbIds: data.related_donors_db_ids,
    allMessages: parseAllMessages(data.all_messages),
  };
};

export const parseRecipientRequirements = (data: RecipientRequirementsGenerated): RecipientRequirements => {
  const {
    require_better_match_in_compatibility_index,
    require_better_match_in_compatibility_index_or_blood_group,
    require_compatible_blood_group,
    max_donor_age,
    max_donor_height,
    max_donor_weight,
    min_donor_age,
    min_donor_height,
    min_donor_weight,
  } = data;

  return {
    requireBetterMatchInCompatibilityIndex: require_better_match_in_compatibility_index,
    requireBetterMatchInCompatibilityIndexOrBloodGroup: require_better_match_in_compatibility_index_or_blood_group,
    requireCompatibleBloodGroup: require_compatible_blood_group,
    maxDonorAge: max_donor_age ?? 0,
    maxDonorHeight: max_donor_height ?? 0,
    maxDonorWeight: max_donor_weight ?? 0,
    minDonorAge: min_donor_age ?? 0,
    minDonorHeight: min_donor_height ?? 0,
    minDonorWeight: min_donor_weight ?? 0,
  };
};

export const parseDate = (data: string): Date => {
  return new Date(data);
};

export const parseUpdatedRecipient = (data: UpdatedRecipientGenerated): UpdatedRecipient => {
  return {
    recipient: parseRecipient(data.recipient),
    parsingIssues: data.parsing_issues.map(parseParsingIssuePublic),
  };
};
