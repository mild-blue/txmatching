import { RecipientGenerated, RecipientRequirementsGenerated } from '../generated';
import { Recipient, RecipientRequirements } from '../model';
import { parseBloodGroup, parsePatient } from './patient.parsers';
import { parseAntibodiesPerGroup, parseAntibody, parseAntibodyRaw } from './hla.parsers';

export const parseRecipient = (data: RecipientGenerated): Recipient => {
  return {
    ...parsePatient(data),
    acceptable_blood_groups: data.acceptable_blood_groups?.map(parseBloodGroup) ?? [],
    // TODO: https://github.com/mild-blue/txmatching/issues/401 create hla_antibodies model
    hla_antibodies: {
      hla_antibodies_list: data.hla_antibodies?.hla_antibodies_list.map(parseAntibody) ?? [],
      hla_antibodies_raw_list: data.hla_antibodies?.hla_antibodies_raw_list.map(parseAntibodyRaw) ?? [],
      hla_antibodies_per_groups: data.hla_antibodies?.hla_antibodies_per_groups.map(parseAntibodiesPerGroup) ?? []
    },
    cutoff: data.recipient_cutoff,
    waitingSince: data.waiting_since ? parseDate(data.waiting_since) : undefined,
    previousTransplants: data.previous_transplants,
    recipient_requirements: data.recipient_requirements && parseRecipientRequirements(data.recipient_requirements),
    related_donor_db_id: data.related_donor_db_id
  };
};

export const parseRecipientRequirements = (data: RecipientRequirementsGenerated): RecipientRequirements => {
  const {
    require_better_match_in_compatibility_index,
    require_better_match_in_compatibility_index_or_blood_group,
    require_compatible_blood_group
  } = data;

  return {
    require_better_match_in_compatibility_index,
    require_better_match_in_compatibility_index_or_blood_group,
    require_compatible_blood_group
  };
};

export const parseDate = (data: string): Date => {
  return new Date(data);
};
