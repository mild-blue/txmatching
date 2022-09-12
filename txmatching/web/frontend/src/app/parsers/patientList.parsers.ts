import { PatientsGenerated } from "../generated";
import { PatientList } from "../model";
import { parseDonor } from "./donor.parsers";
import { parseRecipient } from "./recipient.parsers";

export const parsePatientList = (data: PatientsGenerated): PatientList => {
  return {
    donors: data.donors?.map(parseDonor) ?? [],
    recipients: data.recipients?.map(parseRecipient) ?? [],
  };
};
