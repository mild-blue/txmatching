import { Component, Input } from '@angular/core';
import { PatientService } from '@app/services/patient/patient.service';
import { Configuration } from '@app/model/Configuration';
import { DetailedScorePerGroup, HlaMatchType } from '@app/model/Hla';
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
  @Input() detailedScorePerGroup?: DetailedScorePerGroup[];

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
}
