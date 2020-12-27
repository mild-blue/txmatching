import { Component, Input, OnInit } from '@angular/core';
import { PatientService } from '@app/services/patient/patient.service';
import { compatibleBloodGroups } from '@app/model/Patient';
import { Configuration } from '@app/model/Configuration';
import { PatientList } from '@app/model/PatientList';
import { DetailedCompatibilityIndex, HlaMatchType } from '@app/model/Hla';
import { Transplant } from '@app/model/Transplant';

@Component({
  selector: 'app-matching-transplant',
  templateUrl: './matching-transplant.component.html',
  styleUrls: ['./matching-transplant.component.scss']
})
export class MatchingTransplantComponent implements OnInit {

  @Input() configuration?: Configuration;
  @Input() transplant?: Transplant;
  @Input() patients?: PatientList;

  @Input() score?: number;
  @Input() detailedCompatibilityIndex?: DetailedCompatibilityIndex[];

  constructor(private _patientService: PatientService) {
  }

  ngOnInit() {
  }

  get pairBloodCompatible(): boolean {
    if (!this.transplant) {
      return false;
    }

    return compatibleBloodGroups[this.transplant.r.parameters.blood_group].includes(this.transplant.d.parameters.blood_group);
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
    const recipientAntibodiesGroups = this.transplant?.r.hla_antibodies.hla_codes_over_cutoff_per_group;
    if (!recipientAntibodiesGroups) {
      return [];
    }

    const currentGroup = recipientAntibodiesGroups.find(g => g.hla_group === group);
    return currentGroup?.hla_codes ?? [];
  }
}
