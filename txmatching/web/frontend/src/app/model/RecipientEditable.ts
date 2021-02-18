import { PatientEditable } from '@app/model/PatientEditable';
import { AntibodyEditable } from '@app/model/Hla';

export class RecipientEditable extends PatientEditable {
  acceptableBloodGroups: string[] = [];
  antibodies: AntibodyEditable[] = [];
  antibodiesCutoff: number = 2000;
  waitingSince: Date = new Date();
  previousTransplants: number = 0;

  removeAntibody(a: AntibodyEditable) {
    const index = this.antibodies.indexOf(a);
    if (index !== -1) {
      this.antibodies.splice(index, 1);
    }
  }
}
