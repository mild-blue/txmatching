import { Component, Input, OnInit } from '@angular/core';
import { Transplant } from '@app/model/Matching';
import { PatientService } from '@app/services/patient/patient.service';
import { Subscription } from 'rxjs';
import { first } from 'rxjs/operators';
import { compatibleBloodGroups, Patient } from '@app/model/Patient';

@Component({
  selector: 'app-matching-transplant',
  templateUrl: './matching-transplant.component.html',
  styleUrls: ['./matching-transplant.component.scss']
})
export class MatchingTransplantComponent implements OnInit {

  @Input() transplant?: Transplant;

  private _patients: Patient[] = [];
  private _patientsSubscription?: Subscription;

  private _donor?: Patient;
  private _recipient?: Patient;
  private _matchingAntigens?: string[];

  constructor(private _patientService: PatientService) {
  }

  get donor(): Patient | undefined {
    if (!this._donor) {
      this._donor = this._patients.find(p => p.medical_id === this.transplant?.donor);
    }
    return this._donor;
  }

  get recipient(): Patient | undefined {
    if (!this._recipient) {
      this._recipient = this._patients.find(p => p.medical_id === this.transplant?.recipient);
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

  ngOnInit(): void {
    this._loadPatients();
  }

  public countryImage(country: string): string {
    return `../../../assets/img/countries/${country}.png`;
  }

  public antigenScore(prefix: string): number {
    return this.matchingAntigens ? this.matchingAntigens.filter(a => a.startsWith(prefix)).length : 0;
  }

  private _loadPatients(): void {
    this._patientsSubscription = this._patientService.getPatients()
    .pipe(first())
    .subscribe((patients: Patient[]) => this._patients = patients);
  }
}
