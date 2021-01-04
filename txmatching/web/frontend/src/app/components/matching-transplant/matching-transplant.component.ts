import { Component, Input } from '@angular/core';
import { PatientService } from '@app/services/patient/patient.service';
import { Configuration } from '@app/model/Configuration';
import { AntibodyMatchType, DetailedScorePerGroup, AntigenMatchType } from '@app/model/Hla';
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

  public getAntigenMatchClass(match: AntigenMatchType): string {
    if (match === AntigenMatchType.BROAD || match === AntigenMatchType.HIGH_RES || match === AntigenMatchType.SPLIT) {
      // donor antigen matches some recipient antigen
      return 'matching';
    }

    return '';
  }

  public getAntibodyMatchClass(match: AntibodyMatchType): string {
    if (match === AntibodyMatchType.MATCH) {
      // recipient antibody matches some donor antigen
      return 'bad-matching';
    }

    return '';
  }
}
