import { Component, Input, OnInit } from '@angular/core';
import { PatientService } from '@app/services/patient/patient.service';
import { antibodiesMultipliers, compatibleBloodGroups } from '@app/model/Patient';
import { Configuration } from '@app/model/Configuration';
import { PatientList } from '@app/model/PatientList';
import { Hla, HlaGroupCodes } from '@app/model/Hla';
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

  public hlaScores?: Map<string, number>;
  public totalScore: number = 0;

  constructor(private _patientService: PatientService) {
  }

  ngOnInit() {
    this._initHLAScores();
    this._initTotalScore();
  }

  public getGroupCodes(groups: HlaGroupCodes[], group: string): string[] {
    const currentGroup = groups.find(g => g.hla_group === group);

    return currentGroup?.hla_codes ?? [];
  }

  get prefixes(): string[] {
    return Object.keys(antibodiesMultipliers);
  }

  get pairBloodCompatible(): boolean {
    if (!this.transplant) {
      return false;
    }

    return compatibleBloodGroups[this.transplant.r.parameters.blood_group].includes(this.transplant.d.parameters.blood_group);
  }

  public filterCodes(codes: Hla[], prefix: string): Hla[] {
    return codes.filter(code => code.code?.startsWith(prefix));
  }

  public filterPureCodes(codes: string[], prefix: string): string[] {
    return codes.filter(code => code.startsWith(prefix));
  }

  public otherHLA(codes: Hla[]): Hla[] {
    // return codes that do not start with any of prefixes
    return codes.filter(i => {
      for (const prefix of this.prefixes) {
        if (!i.code || i.code.startsWith(prefix)) {
          return false;
        }
      }
      return true;
    });
  }

  public otherHLAPure(codes: string[]): string[] {
    // return codes that do not start with any of prefixes
    return codes.filter(i => {
      for (const prefix of this.prefixes) {
        if (i.startsWith(prefix)) {
          return false;
        }
      }
      return true;
    });
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

  private _initHLAScores(): void {

    if (!this.transplant?.d || !this.transplant?.r) {
      return;
    }

    const donorAntigensCodes = this.transplant.d.parameters.hla_typing.hla_types_list.map(a => a.code);
    const recipientAntigensCodes = this.transplant.r.parameters.hla_typing.hla_types_list.map(a => a.code);
    const recipientAntibodiesCodes = this.transplant.r.hla_antibodies.hla_codes_over_cutoff.map(a => a);
    const matchingAntigens = donorAntigensCodes.filter(a => recipientAntigensCodes.includes(a));
    const matchingAntibodies = recipientAntibodiesCodes.filter(a => donorAntigensCodes.includes(a));

    const map: Map<string, number> = new Map<string, number>();
    for (const prefix of this.prefixes) {
      const prefixBadMatch = matchingAntibodies.length ? matchingAntibodies.filter(a => a?.startsWith(prefix)).length : false;

      if (prefixBadMatch) {
        map.set(prefix, -1);
        continue;
      }

      const score = matchingAntigens ? matchingAntigens.filter(a => a?.startsWith(prefix)).length * antibodiesMultipliers[prefix] : 0;
      map.set(prefix, score);
    }

    this.hlaScores = map;
    this.totalScore = [...this.hlaScores.values()].reduce((a, b) => a + b, 0);
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

    // sum all scores for matching antigens
    if (this.hlaScores) {
      this.totalScore = [...this.hlaScores.values()].reduce((a, b) => a + b, 0);
    }
  }
}
