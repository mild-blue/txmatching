import { Component, Input } from '@angular/core';
import { Transplant } from '@app/model/Matching';
import { PatientService } from '@app/services/patient/patient.service';
import { antibodiesMultipliers, compatibleBloodGroups, Patient } from '@app/model/Patient';
import { faAngleRight } from '@fortawesome/free-solid-svg-icons';

@Component({
  selector: 'app-matching-transplant',
  templateUrl: './matching-transplant.component.html',
  styleUrls: ['./matching-transplant.component.scss']
})
export class MatchingTransplantComponent {

  private _donor?: Patient;
  private _recipient?: Patient;
  private _matchingAntigens?: string[];

  @Input() transplant?: Transplant;
  @Input() patients: Patient[] = [];

  public arrowRight = faAngleRight;

  constructor(private _patientService: PatientService) {
  }

  get donor(): Patient | undefined {
    if (!this._donor) {
      this._donor = this.patients.find(p => p.medical_id === this.transplant?.donor);
    }
    return this._donor;
  }

  get recipient(): Patient | undefined {
    if (!this._recipient) {
      this._recipient = this.patients.find(p => p.medical_id === this.transplant?.recipient);
    }
    return this._recipient;
  }

  get matchingAntigens(): string[] | undefined {
    if (this.donor && this.recipient && this._matchingAntigens === undefined) {
      const donorAntigens = this.donor.parameters.hla_antigens.codes;
      const recipientAntigens = this.recipient.parameters.hla_antigens.codes;
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

  get antibodies(): string[] {
    return Object.keys(antibodiesMultipliers);
  }

  public antigenScore(prefix: string): number {
    return this.matchingAntigens ? this.matchingAntigens.filter(a => a.startsWith(prefix)).length * antibodiesMultipliers[prefix] : 0;
  }

  public filterCodes(codes: string[], prefix: string): string[] {
    return codes.filter(code => code.startsWith(prefix));
  }
}
