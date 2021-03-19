import { Component, ElementRef, Input, OnInit, ViewChild } from '@angular/core';
import { Patient } from '@app/model/Patient';
import { Configuration, DonorRecipientScore } from '@app/model/Configuration';
import { FormControl, FormGroup, NgForm, Validators } from '@angular/forms';
import { Observable } from 'rxjs';
import { map, startWith } from 'rxjs/operators';
import { ControlErrorStateMatcher, patientFullTextSearch, patientNameValidator } from '@app/directives/validators/form.directive';
import { Donor } from '@app/model/Donor';
import { Recipient } from '@app/model/Recipient';
import { PatientList } from '@app/model/PatientList';
import { AbstractFormHandlerComponent } from '@app/components/abstract-form-handler/abstract-form-handler.component';

@Component({
  selector: 'app-configuration-scores',
  templateUrl: './configuration-scores.component.html',
  styleUrls: ['./configuration-scores.component.scss']
})
export class ConfigurationScoresComponent extends AbstractFormHandlerComponent implements OnInit {
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

  public errorMatcher = new ControlErrorStateMatcher();

  constructor() {
    super();

    this.filteredDonors = this.form.controls.donor.valueChanges.pipe(
      startWith(''),
      map((value: string | Donor | Recipient | null) => {
        return !value || typeof value === 'string' ? value : value.medicalId;
      }),
      map(name => name ? patientFullTextSearch(this.donors, name) : this.donors.slice())
    );

    this.filteredRecipients = this.form.controls.recipient.valueChanges.pipe(
      startWith(''),
      map((value: string | Donor | Recipient) => {
        return !value || typeof value === 'string' ? value : value.medicalId;
      }),
      map(name => name ? patientFullTextSearch(this.recipients, name) : this.recipients.slice())
    );
  }

  ngOnInit() {
    this.form.controls.donor.setValidators(patientNameValidator(this.donors));
    this.form.controls.recipient.setValidators(patientNameValidator(this.recipients));
  }

  get donors(): Patient[] {
    return this.patients?.donors ?? [];
  }

  get recipients(): Patient[] {
    return this.patients?.recipients ?? [];
  }

  get selectedScores(): DonorRecipientScore[] {
    return this.configuration?.manual_donor_recipient_scores ?? [];
  }

  public addScore(): void {
    if (this.form.pristine || this.form.untouched || !this.form.valid) {
      return;
    }

    const { donor, recipient, score } = this.form.value;

    this.configuration?.manual_donor_recipient_scores.push({
      donor_db_id: donor.dbId,
      recipient_db_id: recipient.dbId,
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
    return this.patients?.donors.find(p => p.dbId === id);
  }

  public getRecipientByDbId(id: number): Recipient | undefined {
    return this.patients?.recipients.find(p => p.dbId === id);
  }

  get donor(): Donor | undefined {
    return this.form.controls.donor.value;
  }

  get recipient(): Recipient | undefined {
    return this.form.controls.recipient.value;
  }

  public displayFn(user: Donor | Recipient): string {
    return user?.medicalId ? user.medicalId : '';
  }
}
