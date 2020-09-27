import { Component, Input, OnInit } from '@angular/core';
import { Transplant } from '@app/model/Matching';
import { PatientService } from '@app/services/patient/patient.service';
import { antibodiesMultipliers, PatientList } from '@app/model/Patient';

@Component({
  selector: 'app-matching-transplant',
  templateUrl: './matching-transplant.component.html',
  styleUrls: ['./matching-transplant.component.scss']
})
export class MatchingTransplantComponent implements OnInit {

  @Input() transplant?: Transplant;
  @Input() patients?: PatientList;

  public hlaScores?: Map<string, number>;
  public hlaScoresTotal: number = 0;

  constructor(private _patientService: PatientService) {
  }

  ngOnInit() {
    this._initHLAScores();
  }

  get prefixes(): string[] {
    return Object.keys(antibodiesMultipliers);
  }

  public filterCodes(codes: string[], prefix: string): string[] {
    return codes.filter(code => code.startsWith(prefix));
  }

  public otherHLA(codes: string[]): string[] {
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

  public getDonorAntigenClass(code: string): string {
    if (!this.transplant || !this.transplant.r) {
      return '';
    }

    if (this.transplant.r.hla_antibodies.hla_codes_over_cutoff.includes(code)) {
      // donor antigen matches some recipient antibody
      return 'bad-matching';
    }

    if (this.transplant.r.parameters.hla_typing.codes.includes(code)) {
      // donor antigen matches some recipient antigen
      return 'matching';
    }

    return '';
  }

  public getRecipientAntigenClass(code: string): string {
    if (this.transplant && this.transplant.d && this.transplant.r
      && this.transplant.d.parameters.hla_typing.codes.includes(code)
      && !this.transplant.r.hla_antibodies.hla_codes_over_cutoff.includes(code)) {
      // recipient antigen matches some donor antigen
      // and code is not recipient antibody
      return 'matching';
    }
    return '';
  }

  public getRecipientAntibodyClass(code: string): string {
    if (this.transplant && this.transplant.d && this.transplant.d.parameters.hla_typing.codes.includes(code)) {
      // recipient antibody matches some donor antigen
      return 'bad-matching';
    }
    return '';
  }

  private _initHLAScores(): void {

    if (!this.transplant || !this.transplant.d || !this.transplant.r) {
      return;
    }

    const donorAntigens = this.transplant.d.parameters.hla_typing.codes;
    const recipientAntigens = this.transplant.r.parameters.hla_typing.codes;
    const matchingAntigens = donorAntigens.filter(a => recipientAntigens.includes(a));

    if (!matchingAntigens.length) {
      return;
    }

    const map: Map<string, number> = new Map<string, number>();
    for (const prefix of this.prefixes) {
      const score = matchingAntigens.filter(a => a.startsWith(prefix)).length * antibodiesMultipliers[prefix];
      map.set(prefix, score);
    }

    this.hlaScores = map;
    this.hlaScoresTotal = [...this.hlaScores.values()].reduce((a, b) => a + b, 0);
  }
}
