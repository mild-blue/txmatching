import { PatientEditable } from '@app/model/PatientEditable';
import { Recipient, RecipientRequirements } from '@app/model/Recipient';
import { AntibodyEditable } from '@app/model/Hla';

export class RecipientEditable extends PatientEditable {
  acceptableBloodGroups: string[] = [];
  antibodies: AntibodyEditable[] = [];
  antibodiesCutoff: number = 2000;
  waitingSince: Date = new Date();
  previousTransplants: number = 0;
  recipientRequirements: RecipientRequirements = {
    require_better_match_in_compatibility_index: false,
    require_better_match_in_compatibility_index_or_blood_group: false,
    require_compatible_blood_group: false
  };

  initializeFromPatient(recipient: Recipient) {
    super.initializeFromPatient(recipient);
    this.acceptableBloodGroups = recipient.acceptable_blood_groups;
    this.antibodies = recipient.hla_antibodies.hla_antibodies_list;
    this.antibodiesCutoff = 2000; // TODOO
    //this.waitingSince
    //this.previousTransplants
    if (recipient.recipient_requirements) {
      this.recipientRequirements = recipient.recipient_requirements;
    }
    // TODOO
  }

  removeAntibody(a: AntibodyEditable) {
    const index = this.antibodies.indexOf(a);
    if (index !== -1) {
      this.antibodies.splice(index, 1);
    }
  }
}
