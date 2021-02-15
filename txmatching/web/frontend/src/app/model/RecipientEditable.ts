import { Antibody } from './Hla';
import { PatientEditable } from '@app/model/PatientEditable';

export class RecipientEditable extends PatientEditable {
  acceptableBloodGroups: string[] = [];
  antibodies: Antibody[] = [];
  // eslint-disable-next-line no-magic-numbers
  antibodiesCutoff: number = 2000;
  waitingSince: Date = new Date();
  previousTransplants: number = 0;

  removeAntibody(a: Antibody) {
    const index = this.antibodies.indexOf(a);
    if (index !== -1) {
      this.antibodies.splice(index, 1);
    }
  }
}
