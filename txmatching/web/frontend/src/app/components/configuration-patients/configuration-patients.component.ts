import { Component, Input } from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { Patient, PatientList } from '@app/model/Patient';
import { faPlus, faTimes } from '@fortawesome/free-solid-svg-icons';
import { Configuration } from '@app/model/Configuration';

@Component({
  selector: 'app-configuration-patients',
  templateUrl: './configuration-patients.component.html',
  styleUrls: ['./configuration-patients.component.scss']
})
export class ConfigurationPatientsComponent {
  @Input() patients?: PatientList;
  @Input() configuration?: Configuration;

  public plusIcon = faPlus;
  public closeIcon = faTimes;

  public placeholder: string = 'Search patient';
  public keyword = 'medical_id';

  public requiredPatientsForm: FormGroup = new FormGroup({
    patient: new FormControl('', Validators.required)
  });

  get availablePatients(): Patient[] {
    if (!this.patients || !this.configuration) {
      return [];
    }
    const requiredIds = this.configuration?.required_patient_db_ids;
    const allPatients = [...this.patients.donors, ...this.patients.recipients];
    const uniquePatients = [...new Set(allPatients)]; // only unique
    return uniquePatients.filter(p => !requiredIds.includes(p.db_id)); // not already in config
  }

  public addRequiredPatient(): void {
    const controls = this.requiredPatientsForm.controls;

    const patient = controls.patient.value;

    if (!this.configuration || !patient || !patient.db_id) {
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
}
