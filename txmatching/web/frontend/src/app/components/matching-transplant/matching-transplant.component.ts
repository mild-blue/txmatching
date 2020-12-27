import { Component, Input } from '@angular/core';
import { PatientService } from '@app/services/patient/patient.service';
import { Configuration } from '@app/model/Configuration';
import { DetailedCompatibilityIndex, HlaMatchType } from '@app/model/Hla';
import { Recipient } from '@app/model/Recipient';
import { Donor } from '@app/model/Donor';

@Component({
  selector: 'app-matching-transplant',
  templateUrl: './matching-transplant.component.html',
  styleUrls: ['./matching-transplant.component.scss']
})
export class MatchingTransplantComponent {

  @Input() configuration?: Configuration;

  @Input() score?: number;
  @Input() donor?: Donor;
  @Input() recipient?: Recipient;
  @Input() isBloodCompatible?: boolean;
  @Input() detailedCompatibilityIndex?: DetailedCompatibilityIndex[];

  constructor(private _patientService: PatientService) {
  }

  public getHlaClass(match: HlaMatchType): string {
    if (match === HlaMatchType.ANTIBODY) {
      // donor antigen matches some recipient antibody
      return 'bad-matching';
    }

    if (match === HlaMatchType.BROAD || match === HlaMatchType.HIGH_RES || match === HlaMatchType.SPLIT) {
      // donor antigen matches some recipient antigen
      return 'matching';
    }

    return '';
  }

  public getAntibodiesCodes(group: string): string[] {
    const recipientAntibodiesGroups = this.recipient?.hla_antibodies.hla_codes_over_cutoff_per_group;
    if (!recipientAntibodiesGroups) {
      return [];
    }

    const currentGroup = recipientAntibodiesGroups.find(g => g.hla_group === group);
    return currentGroup?.hla_codes ?? [];
  }
}
