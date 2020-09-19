import { Component, Input } from '@angular/core';
import { Patient, PatientList } from '@app/model/Patient';
import { Configuration, DonorRecipientScore } from '@app/model/Configuration';
import { FormControl } from '@angular/forms';
import { Observable } from 'rxjs';
import { map, startWith } from 'rxjs/operators';

@Component({
  selector: 'app-configuration-scores',
  templateUrl: './configuration-scores.component.html',
  styleUrls: ['./configuration-scores.component.scss']
})
export class ConfigurationScoresComponent {
  @Input() patients?: PatientList;
  @Input() configuration?: Configuration;

  public donorFormControl = new FormControl('');
  public recipientFormControl = new FormControl('');

  public filteredDonors: Observable<Patient[]>;
  public filteredRecipients: Observable<Patient[]>;

  constructor() {
    this.filteredDonors = this.donorFormControl.valueChanges.pipe(
      startWith(''),
      map((value: string | Patient) => {
        return typeof value === 'string' ? value : value.medical_id;
      }),
      map(name => name ? this._filter(this.donors, name) : this.donors.slice())
    );

    this.filteredRecipients = this.recipientFormControl.valueChanges.pipe(
      startWith(''),
      map((value: string | Patient) => {
        return typeof value === 'string' ? value : value.medical_id;
      }),
      map(name => name ? this._filter(this.recipients, name) : this.recipients.slice())
    );
  }

  get donors(): Patient[] {
    return this.patients ? this.patients.donors : [];
  }

  get recipients(): Patient[] {
    return this.patients ? this.patients.recipients : [];
  }

  get selectedScores(): DonorRecipientScore[] {
    return this.configuration ? this.configuration.manual_donor_recipient_scores : [];
  }

  public setDonor(score: DonorRecipientScore, patient: Patient, input: HTMLInputElement): void {
    score.donor = patient.db_id;

    // Reset input
    this.donorFormControl.setValue('');
    input.value = '';
  }

  public setRecipient(score: DonorRecipientScore, patient: Patient, input: HTMLInputElement): void {
    score.recipient = patient.db_id;

    // Reset input
    this.recipientFormControl.setValue('');
    input.value = '';
  }

  public setScore(score: DonorRecipientScore, event: Event): void {
    const input = event.target as HTMLInputElement;
    score.score = +input.value;
  }

  public addScore(): void {
    this.configuration?.manual_donor_recipient_scores.push({});
  }

  public removeScore(s: DonorRecipientScore): void {
    if (!this.configuration) {
      return;
    }
    const scores = this.configuration.manual_donor_recipient_scores;
    const index = scores.indexOf(s);

    if (index >= 0) {
      scores.splice(index, 1);
    }
  }

  public getDonorByDbId(id: number): string {
    const donor = this.patients?.donors.find(p => p.db_id === id);
    return donor ? donor.medical_id : '';
  }

  public getRecipientByDbId(id: number): string {
    const recipient = this.patients?.recipients.find(p => p.db_id === id);
    return recipient ? recipient.medical_id : '';
  }

  public displayFn(user: Patient): string {
    return user && user.medical_id ? user.medical_id : '';
  }

  // todo fulltext
  // filter while typing
  private _filter(list: Patient[], name: string): Patient[] {
    const filterValue = name.toLowerCase();
    return list.filter(option => option.medical_id.toLowerCase().indexOf(filterValue) === 0);
  }
}
