import { RecipientGenerated, RecipientRequirementsGenerated, UpdatedRecipientGenerated } from '../generated';
import { Recipient, RecipientRequirements, UpdatedRecipient } from '../model';
import { parseBloodGroup, parsePatient } from './patient.parsers';
import { parseAntibodies } from './hla.parsers';
import { ListItem } from '@app/components/list-item/list-item.interface';
import { PatientPairItemComponent } from '@app/components/patient-pair-item/patient-pair-item.component';
import { PatientPairDetailComponent } from '@app/components/patient-pair-detail/patient-pair-detail.component';
import { parseParsingError } from '@app/parsers/parsingError.parsers';

export const parseRecipient = (data: RecipientGenerated): Recipient => {
  const recipientListItem: ListItem = {
    index: 0,
    isActive: false,
    itemComponent: PatientPairItemComponent,
    detailComponent: PatientPairDetailComponent
  };

  return {
    ...parsePatient(data, recipientListItem),
    acceptableBloodGroups: data.acceptable_blood_groups?.map(parseBloodGroup) ?? [],
    hlaAntibodies: parseAntibodies(data.hla_antibodies),
    cutoff: data.recipient_cutoff,
    waitingSince: data.waiting_since ? parseDate(data.waiting_since) : undefined,
    previousTransplants: data.previous_transplants,
    recipientRequirements: data.recipient_requirements && parseRecipientRequirements(data.recipient_requirements),
    relatedDonorDbId: data.related_donor_db_id
  };
};

export const parseRecipientRequirements = (data: RecipientRequirementsGenerated): RecipientRequirements => {
  const {
    require_better_match_in_compatibility_index,
    require_better_match_in_compatibility_index_or_blood_group,
    require_compatible_blood_group
  } = data;

  return {
    requireBetterMatchInCompatibilityIndex: require_better_match_in_compatibility_index,
    requireBetterMatchInCompatibilityIndexOrBloodGroup: require_better_match_in_compatibility_index_or_blood_group,
    requireCompatibleBloodGroup: require_compatible_blood_group
  };
};

export const parseDate = (data: string): Date => {
  return new Date(data);
};

export const parseUpdatedRecipient = (data: UpdatedRecipientGenerated): UpdatedRecipient => {
  return {
    recipient: parseRecipient(data.recipient),
    parsingErrors: data.parsing_errors.map(parseParsingError)
  };
};
