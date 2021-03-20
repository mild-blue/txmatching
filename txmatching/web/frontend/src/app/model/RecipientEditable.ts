import { PatientEditable } from '@app/model/PatientEditable';
import { Recipient, RecipientRequirements } from '@app/model/Recipient';
import { BloodGroup } from '@app/model/enums/BloodGroup';
import { AntibodyEditable } from '@app/model/HlaEditable';

export class RecipientEditable extends PatientEditable {
  acceptableBloodGroups: BloodGroup[] = [];
  antibodies: AntibodyEditable[] = [];
  antibodiesCutoff?: number = 2000;
  waitingSince?: Date = new Date();
  previousTransplants?: number = 0;
  recipientRequirements: RecipientRequirements = {
    requireBetterMatchInCompatibilityIndex: false,
    requireBetterMatchInCompatibilityIndexOrBloodGroup: false,
    requireCompatibleBloodGroup: false
  };

  initializeFromPatient(recipient: Recipient) {
    super.initializeFromPatient(recipient);
    this.acceptableBloodGroups = [...recipient.acceptableBloodGroups];
    this.antibodies = [...recipient.hlaAntibodies.hlaAntibodiesRawList];
    this.antibodiesCutoff = recipient.cutoff;
    this.waitingSince = recipient.waitingSince;
    this.previousTransplants = recipient.previousTransplants;
    if (recipient.recipientRequirements) {
      this.recipientRequirements = recipient.recipientRequirements;
    }
  }

  removeAntibody(a: AntibodyEditable) {
    const index = this.antibodies.indexOf(a);
    if (index !== -1) {
      this.antibodies.splice(index, 1);
    }
  }
}
