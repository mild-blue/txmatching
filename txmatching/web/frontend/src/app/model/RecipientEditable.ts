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
    require_better_match_in_compatibility_index: false,
    require_better_match_in_compatibility_index_or_blood_group: false,
    require_compatible_blood_group: false
  };

  initializeFromPatient(recipient: Recipient) {
    super.initializeFromPatient(recipient);
    this.acceptableBloodGroups = [...recipient.acceptable_blood_groups];
    this.antibodies = [...recipient.hla_antibodies.hla_antibodies_raw_list];
    this.antibodiesCutoff = recipient.cutoff;
    this.waitingSince = recipient.waitingSince;
    this.previousTransplants = recipient.previousTransplants;
    if (recipient.recipient_requirements) {
      this.recipientRequirements = recipient.recipient_requirements;
    }
  }

  removeAntibody(a: AntibodyEditable) {
    const index = this.antibodies.indexOf(a);
    if (index !== -1) {
      this.antibodies.splice(index, 1);
    }
  }
}
