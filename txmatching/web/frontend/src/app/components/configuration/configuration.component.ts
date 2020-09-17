import { Component, EventEmitter, Input, OnInit, Output } from '@angular/core';
import { AbstractControl, FormBuilder, FormControl, FormGroup, Validators } from '@angular/forms';
import { Configuration } from '@app/model/Configuration';
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

  public addManualScore(): void {
    const { donor, recipient, score } = this.manualScoreForm.controls;

    if (!this.configuration || !donor || !recipient || !score) {
      return;
    }

    this.configuration.manual_donor_recipient_scores.push({
      donor: donor.value.db_id,
      recipient: recipient.value.db_id,
      score: score.value
    });
  }

  public submitAction(): void {
    if (this.configForm) {
      this.configSubmitted.emit(this.configForm.value);
    }
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
        console.log('adding', name, value);
        group[name] = new FormControl(value);
      }
    }

    this.configForm = new FormGroup(group);
  }

  get enableManualScore(): boolean {
    const patientsExist = !!this.patients?.recipients && !!this.patients?.donors;
    const configPropertyExists = !!this.configuration?.manual_donor_recipient_scores;
    return patientsExist && configPropertyExists;
  }
}
