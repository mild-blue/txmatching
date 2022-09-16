import { Donor } from "@app/model/Donor";
import { Recipient } from "@app/model/Recipient";

export interface PatientList {
  donors: Donor[];
  recipients: Recipient[];
}
