import { PatientEditable } from '@app/model/PatientEditable';
import { Recipient } from '@app/model/Recipient';
import { AntibodyEditable } from '@app/model/Hla';

export class RecipientEditable extends PatientEditable {
  acceptableBloodGroups: string[] = [];
  antibodies: AntibodyEditable[] = [];
  antibodiesCutoff: number = 2000;
  waitingSince: Date = new Date();
  previousTransplants: number = 0;

  initializeFromPatient(recipient: Recipient) {
    super.initializeFromPatient(recipient);
    this.acceptableBloodGroups = recipient.acceptable_blood_groups;
    this.antibodies = recipient.hla_antibodies.hla_antibodies_list;
    this.antibodiesCutoff = 2000; // TODOO
    //this.waitingSince
    //this.previousTransplants
    // TODOO
  }

  removeAntibody(a: AntibodyEditable) {
    const index = this.antibodies.indexOf(a);
    if (index !== -1) {
      this.antibodies.splice(index, 1);
    }
  }
}
