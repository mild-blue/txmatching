import { Component, EventEmitter, Input, OnInit, Output } from '@angular/core';
import { AbstractControl, FormBuilder, FormControl, FormGroup, Validators } from '@angular/forms';
import { Configuration, CountryCombination, DonorRecipientScore } from '@app/model/Configuration';
import { faPlus, faTimes } from '@fortawesome/free-solid-svg-icons';
import { PatientList } from '@app/model/Patient';

@Component({
  selector: 'app-configuration',
  templateUrl: './configuration.component.html',
  styleUrls: ['./configuration.component.scss']
})
export class ConfigurationComponent implements OnInit {

  @Input() isOpened: boolean = false;
  @Input() configuration?: Configuration;
  @Input() patients?: PatientList;
  @Output() configSubmitted: EventEmitter<Configuration> = new EventEmitter<Configuration>();
  @Output() configClosed: EventEmitter<void> = new EventEmitter<void>();

  // forms
  public configForm?: FormGroup;
  public manualScoreForm: FormGroup = new FormGroup({
    donor: new FormControl('', Validators.required),
    recipient: new FormControl('', Validators.required),
    score: new FormControl('', Validators.required)
  });
  public countriesForm: FormGroup = new FormGroup({
    donorCountry: new FormControl('', Validators.required),
    recipientCountry: new FormControl('', Validators.required)
  });
  public requiredPatientsForm: FormGroup = new FormGroup({
    patient: new FormControl('', Validators.required)
  });

  // icons
  public closeIcon = faTimes;
  public plusIcon = faPlus;

  constructor(private _formBuilder: FormBuilder) {
  }

  ngOnInit(): void {
    this._buildFormFromConfig();
  }

  get showManualScore(): boolean {
    const patientsExist = !!this.patients?.recipients && !!this.patients?.donors;
    const configPropertyExists = !!this.configuration?.manual_donor_recipient_scores;
    return patientsExist && configPropertyExists;
  }

  get donorCountries(): string[] {
    if (!this.patients || !this.patients.donors) {
      return [];
    }
    const countries = this.patients.donors.map(p => p.parameters.country_code);
    return [...new Set(countries)]; // only unique
  }

  get recipientCountries(): string[] {
    if (!this.patients || !this.patients.recipients) {
      return [];
    }
    const countries = this.patients.recipients.map(p => p.parameters.country_code);
    return [...new Set(countries)]; // only unique
  }

  public addManualScore(): void {
    const controls = this.manualScoreForm.controls;

    const donor = controls.donor.value;
    const recipient = controls.recipient.value;
    const score = controls.score.value;

    if (!this.configuration || !donor || !recipient || !score) {
      return;
    }

    this.configuration.manual_donor_recipient_scores.push({
      donor: donor.db_id,
      recipient: donor.db_id,
      score
    });

    this.manualScoreForm.reset();
  }

  public removeManualScore(item: DonorRecipientScore): void {
    if (!this.configuration) {
      return;
    }
    const scores = this.configuration.manual_donor_recipient_scores;
    const index = scores.indexOf(item);
    scores.splice(index, 1);
  }

  public addCountryCombination(): void {
    const controls = this.countriesForm.controls;

    const donorCountry = controls.donorCountry.value;
    const recipientCountry = controls.recipientCountry.value;

    if (!this.configuration || !donorCountry || !recipientCountry) {
      return;
    }

    this.configuration.forbidden_country_combinations.push({
      donor_country: donorCountry,
      recipient_country: recipientCountry
    });

    this.countriesForm.reset();
  }

  public removeCountryCombination(item: CountryCombination): void {
    if (!this.configuration) {
      return;
    }
    const countries = this.configuration.forbidden_country_combinations;
    const index = countries.indexOf(item);

    if (index >= 0) {
      countries.splice(index, 1);
    }
  }

  public addRequiredPatient(): void {
    const controls = this.requiredPatientsForm.controls;

    const patient = controls.patient.value;

    if (!this.configuration || !patient) {
      return;
    }

    this.configuration.required_patient_db_ids.push(patient.db_id);

    this.requiredPatientsForm.reset();
  }

  public removePatient(id: number): void {
    if (!this.configuration) {
      return;
    }
    const ids = this.configuration.required_patient_db_ids;
    const index = ids.indexOf(id);
    ids.splice(index, 1);
  }

  public close(): void {
    this.configClosed.emit();
  }

  public submitAction(): void {
    if (this.configForm && this.configuration) {
      this.configSubmitted.emit({
        ...this.configForm.value
        // todo add complex UI values, check if valid
        // manual_donor_recipient_scores: this.configuration.manual_donor_recipient_scores
      });
    }
  }

  public getDonor(id: number): string {
    const donor = this.patients?.donors.find(p => p.db_id === id);
    return donor ? donor.medical_id : '';
  }

  public getRecipient(id: number): string {
    const recipient = this.patients?.recipients.find(p => p.db_id === id);
    return recipient ? recipient.medical_id : '';
  }

  private _buildFormFromConfig(): void {
    if (!this.configuration) {
      return;
    }

    const group: { [key: string]: AbstractControl; } = {};

    const names: string[] = Object.keys(this.configuration);
    console.log(this.configuration);
    for (const name of names) {
      const value = this.configuration[name];
      // check if value is primitive
      if (value !== Object(value)) {
        group[name] = new FormControl(value);
      }
    }

    this.configForm = new FormGroup(group);
  }
}
