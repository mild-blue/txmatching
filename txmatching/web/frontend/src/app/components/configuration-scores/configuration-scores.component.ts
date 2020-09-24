import { Component, ElementRef, Input, OnInit, ViewChild } from '@angular/core';
import { Donor, Patient, PatientList, Recipient } from '@app/model/Patient';
import { Configuration, DonorRecipientScore } from '@app/model/Configuration';
import { FormControl, FormGroup, NgForm, Validators } from '@angular/forms';
import { Observable } from 'rxjs';
import { map, startWith } from 'rxjs/operators';
import { ConfigErrorStateMatcher, patientNameValidator } from '@app/directives/validators/configForm.directive';

@Component({
  selector: 'app-configuration-scores',
  templateUrl: './configuration-scores.component.html',
  styleUrls: ['./configuration-scores.component.scss']
})
export class ConfigurationScoresComponent implements OnInit {
  @Input() patients?: PatientList;
  @Input() configuration?: Configuration;

  @ViewChild('viewForm') viewForm?: NgForm;
  @ViewChild('viewDonor') viewDonor?: ElementRef<HTMLInputElement>;
  @ViewChild('viewRecipient') viewRecipient?: ElementRef<HTMLInputElement>;

  public form: FormGroup = new FormGroup({
    donor: new FormControl('', Validators.required),
    recipient: new FormControl('', Validators.required),
    score: new FormControl('', Validators.required)
  });

  public filteredDonors: Observable<Patient[]>;
  public filteredRecipients: Observable<Patient[]>;

  public errorMatcher = new ConfigErrorStateMatcher();

  constructor() {
    this.filteredDonors = this.form.controls.donor.valueChanges.pipe(
      startWith(''),
      map((value: string | Donor | Recipient | null) => {
        return !value || typeof value === 'string' ? value : value.medical_id;
      }),
      map(name => name ? this._filter(this.donors, name) : this.donors.slice())
    );

    this.filteredRecipients = this.form.controls.recipient.valueChanges.pipe(
      startWith(''),
      map((value: string | Donor | Recipient) => {
        return !value || typeof value === 'string' ? value : value.medical_id;
      }),
      map(name => name ? this._filter(this.recipients, name) : this.recipients.slice())
    );
  }

  ngOnInit() {
    this.form.controls.donor.setValidators(patientNameValidator(this.donors));
    this.form.controls.recipient.setValidators(patientNameValidator(this.recipients));
  }

  get donors(): Patient[] {
    return this.patients ? this.patients.donors ?? [] : [];
  }

  get recipients(): Patient[] {
    return this.patients ? this.patients.recipients ?? [] : [];
  }

  get selectedScores(): DonorRecipientScore[] {
    return this.configuration ? this.configuration.manual_donor_recipient_scores : [];
  }

  public addScore(): void {
    if (this.form.pristine || this.form.untouched || !this.form.valid) {
      return;
    }

    const { donor, recipient, score } = this.form.value;

    this.configuration?.manual_donor_recipient_scores.push({
      donor_db_id: donor.db_id,
      recipient_db_id: recipient.db_id,
      score
    });

    // reset form
    this.form.reset();
    this.viewForm?.resetForm('');

    // enable inputs
    if (this.viewDonor) {
      this.viewDonor.nativeElement.disabled = false;
    }
    if (this.viewRecipient) {
      this.viewRecipient.nativeElement.disabled = false;
    }
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

  public getDonorByDbId(id: number): Donor | undefined {
    return this.patients?.donors.find(p => p.db_id === id);
  }

  public getRecipientByDbId(id: number): Recipient | undefined {
    return this.patients?.recipients.find(p => p.db_id === id);
  }

  get donor(): Donor | undefined {
    return this.form.controls.donor.value;
  }

  get recipient(): Recipient | undefined {
    return this.form.controls.recipient.value;
  }

  public handleSelect(control: HTMLInputElement): void {
    if (!control) {
      return;
    }
    control.value = '';
    control.disabled = true;
  }

  public handleRemove(controlName: string, control: HTMLInputElement): void {
    const formControl = this.form.controls[controlName];
    if (!formControl || !control) {
      return;
    }
    formControl.setValue('');
    control.disabled = false;
  }

  public displayFn(user: Donor | Recipient): string {
    return user && user.medical_id ? user.medical_id : '';
  }

  // todo fulltext
  // filter while typing
  private _filter(list: Patient[], name: string): Patient[] {
    const filterValue = name.toLowerCase();
    return list.filter(option => option.medical_id.toLowerCase().indexOf(filterValue) === 0);
  }
}
