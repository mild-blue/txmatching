import { Component, Input } from '@angular/core';
import { Transplant } from '@app/model/Matching';
import { PatientService } from '@app/services/patient/patient.service';
import { antibodiesMultipliers, compatibleBloodGroups, Donor, PatientList, Recipient } from '@app/model/Patient';
import { faAngleRight } from '@fortawesome/free-solid-svg-icons';

@Component({
  selector: 'app-matching-transplant',
  templateUrl: './matching-transplant.component.html',
  styleUrls: ['./matching-transplant.component.scss']
})
export class MatchingTransplantComponent {

  private _donor?: Donor;
  private _recipient?: Recipient;

  @Input() transplant?: Transplant;
  @Input() patients?: PatientList;

  public arrowRight = faAngleRight;

  constructor(private _patientService: PatientService) {
  }

  get donor(): Donor | undefined {
    if (!this._donor && this.patients && this.patients.donors) {
      this._donor = this.patients.donors.find(p => p.medical_id === this.transplant?.donor);
    }
    return this._donor;
  }

  get recipient(): Recipient | undefined {
    if (!this._recipient && this.patients && this.patients.recipients) {
      this._recipient = this.patients.recipients.find(p => p.medical_id === this.transplant?.recipient);
    }
    return this._recipient;
  }

  get isDonorBloodCompatible(): boolean {
    if (!this.donor || !this.recipient) {
      return false;
    }
    const donorBloodGroup = this.donor.parameters.blood_group;
    const recipientBloodGroup = this.recipient.parameters.blood_group;
    return compatibleBloodGroups[recipientBloodGroup].includes(donorBloodGroup);
  }

  get prefixes(): string[] {
    return Object.keys(antibodiesMultipliers);
  }

  public antigenScore(prefix: string): number {
    if (this.donor && this.recipient) {
      const donorAntigens = this.donor.parameters.hla_typing.codes;
      const recipientAntigens = this.recipient.parameters.hla_typing.codes;
      const matchingAntigens = donorAntigens.filter(a => recipientAntigens.includes(a));

      if (matchingAntigens.length) {
        return matchingAntigens.filter(a => a.startsWith(prefix)).length * antibodiesMultipliers[prefix];
      }
    }
    return 0;
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
    if (this.recipient) {
      if (this.recipient.hla_antibodies.hla_codes_over_cutoff.includes(code)) {
        // donor antigen matches some recipient antibody
        return 'bad-matching';
      }

      if (this.recipient.parameters.hla_typing.codes.includes(code)) {
        // donor antigen matches some recipient antigen
        return 'matching';
      }
    }
    return '';
  }

  public getRecipientAntigenClass(code: string): string {
    if (this.donor && this.recipient && this.donor.parameters.hla_typing.codes.includes(code) && !this.recipient.hla_antibodies.hla_codes_over_cutoff.includes(code)) {
      // recipient antigen matches some donor antigen
      // and code is not recipient antibody
      return 'matching';
    }
    return '';
  }

  public getRecipientAntibodyClass(code: string): string {
    if (this.donor && this.donor.parameters.hla_typing.codes.includes(code)) {
      // recipient antibody matches some donor antigen
      return 'bad-matching';
    }
    return '';
  }
}
