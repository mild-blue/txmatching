import { Component, Input, OnInit } from '@angular/core';
import { PatientService } from '@app/services/patient/patient.service';
import { compatibleBloodGroups } from '@app/model/Patient';
import { Transplant } from '@app/model/Transplant';
import { HlaCodesSorted } from '@app/model/Hla';
import { PatientList } from '@app/model/PatientList';

@Component({
  selector: 'app-matching-transplant',
  templateUrl: './matching-transplant.component.html',
  styleUrls: ['./matching-transplant.component.scss']
})
export class MatchingTransplantComponent implements OnInit {

  @Input() transplant?: Transplant;
  @Input() patients?: PatientList;

  public totalScore: number = 0;

  constructor(private _patientService: PatientService) {
  }

  ngOnInit() {
    this._initTotalScore();
  }

  get prefixes(): string[] {
    if (!this.transplant?.donor_antigens) {
      return [];
    }

    return Object.keys(this.transplant.donor_antigens);
  }

  get pairBloodCompatible(): boolean {
    if (!this.transplant) {
      return false;
    }

    return compatibleBloodGroups[this.transplant.r.parameters.blood_group].includes(this.transplant.d.parameters.blood_group);
  }

  public getCodesByPrefix(codes: HlaCodesSorted | undefined, prefix: string): string[] {
    return (codes && codes[prefix]) ?? [];
  }

  public getHlaScoreByPrefix(prefix: string): number {
    return (this.transplant?.antigens_score && this.transplant.antigens_score[prefix]) ?? 0;
  }

  public getDonorAntigenClass(code: string | null): string {
    if (!this.transplant?.r || !code) {
      return '';
    }

    if (this.transplant.r.hla_antibodies.hla_codes_over_cutoff.find(a => a === code)) {
      // donor antigen matches some recipient antibody
      return 'bad-matching';
    }

    if (this.transplant.r.parameters.hla_typing.hla_types_list.find(a => a.code === code)) {
      // donor antigen matches some recipient antigen
      return 'matching';
    }

    return '';
  }

  public getRecipientAntigenClass(code: string | null): string {
    if (this.transplant?.d && this.transplant.r && code
      && this.transplant.d.parameters.hla_typing.hla_types_list.find(a => a.code === code)
      && !this.transplant.r.hla_antibodies.hla_codes_over_cutoff.find(a => a === code)) {
      // recipient antigen matches some donor antigen
      // and code is not recipient antibody
      return 'matching';
    }
    return '';
  }

  public getRecipientAntibodyClass(code: string | null): string {
    if (this.transplant?.d && code && this.transplant.d.parameters.hla_typing.hla_types_list.find(a => a.code === code)) {
      // recipient antibody matches some donor antigen
      return 'bad-matching';
    }
    return '';
  }

  private _initTotalScore(): void {
    // if transplant score exists use it as total score
    if (this.transplant?.score !== undefined) {
      this.totalScore = this.transplant.score;
    }

    // return if there is no donor or recipient object linked
    if (!this.transplant?.d || !this.transplant.r) {
      return;
    }

    // check if there is a match of recipient antibodies and donor antigens
    const donorAntigensCodes = this.transplant.d.parameters.hla_typing.hla_types_list.map(a => a.code);
    for (const antibody of this.transplant.r.hla_antibodies.hla_codes_over_cutoff) {
      if (donorAntigensCodes.includes(antibody)) {
        this.totalScore = -1;
        return;
      }
    }

    // else sum all scores for matching antigens
    if (this.transplant.antigens_score) {
      let sum = 0;
      for (const p of this.prefixes) {
        sum += this.getHlaScoreByPrefix(p);
      }
      this.totalScore = sum;
    }
  }
}
