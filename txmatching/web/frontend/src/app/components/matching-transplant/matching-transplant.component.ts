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
  private _matchingAntigens?: string[];
  private _otherMatchingHLA?: string[];

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

  get matchingAntigens(): string[] | undefined {
    if (this._matchingAntigens === undefined && this.donor && this.recipient) {
      const donorAntigens = this.donor.parameters.hla_typing.codes;
      const recipientAntigens = this.recipient.parameters.hla_typing.codes;
      this._matchingAntigens = donorAntigens.filter(a => recipientAntigens.includes(a));
    }
    return this._matchingAntigens;
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
    return this.matchingAntigens ? this.matchingAntigens.filter(a => a.startsWith(prefix)).length * antibodiesMultipliers[prefix] : 0;
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

  public isAntibodyMatching(code: string): boolean {
    if (this.donor) {
      return this.donor.parameters.hla_typing.codes.includes(code);
    }
    return false;
  }

  get otherMatchingHLA(): string[] | undefined {
    if (this._otherMatchingHLA === undefined && this.donor && this.recipient) {
      const otherDonorHLA = this.otherHLA(this.donor.parameters.hla_typing.codes);
      const otherRecipientHLA = this.otherHLA(this.recipient.parameters.hla_typing.codes);

      this._otherMatchingHLA = otherDonorHLA.filter(a => otherRecipientHLA.includes(a));
    }

    return this._otherMatchingHLA;
  }
}
