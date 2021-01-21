import { TransplantGenerated } from '../generated';
import { PatientList, Transplant } from '../model';
import { parseDetailedScorePerGroup } from './hla.parsers';
import { getPatientPair } from './patientPair.parsers';

export const parseTransplant = (data: TransplantGenerated, patients: PatientList): Transplant => {
  const foundDonor = patients.donors.find(p => p.medical_id === data.donor);
  const foundRecipient = patients.recipients.find(p => p.medical_id === data.recipient);

  return {
    ...getPatientPair(foundDonor, foundRecipient),
    score: data.score,
    compatible_blood: data.compatible_blood,
    donor: data.donor,
    recipient: data.recipient,
    detailed_score_per_group: data.detailed_score_per_group.map(parseDetailedScorePerGroup)
  };
};
