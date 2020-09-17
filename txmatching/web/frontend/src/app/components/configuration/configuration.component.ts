import { Component, EventEmitter, Input, OnInit, Output } from '@angular/core';
import { AbstractControl, FormBuilder, FormControl, FormGroup, Validators } from '@angular/forms';
import { Configuration, DonorRecipientScore } from '@app/model/Configuration';
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

  public addManualScore(): void {
    const { donor, recipient, score } = this.manualScoreForm.controls;

    if (!this.configuration || !donor || !recipient || !score) {
      return;
    }

    this.configuration.manual_donor_recipient_scores.push({
      donor: donor.value,
      recipient: recipient.value,
      score: score.value
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

  public close(): void {
    this.configClosed.emit();
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

  public submitAction(): void {
    if (this.configForm && this.configuration) {
      this.configSubmitted.emit({
        ...this.configForm.value,
        manual_donor_recipient_scores: this.configuration.manual_donor_recipient_scores
      });
    }
  }

  getDonor(id: number): string {
    const donor = this.patients?.donors.find(p => p.db_id === id);
    return donor ? donor.medical_id : '';
  }

  getRecipient(id: number): string {
    const recipient = this.patients?.recipients.find(p => p.db_id === id);
    return recipient ? recipient.medical_id : '';
  }
}
