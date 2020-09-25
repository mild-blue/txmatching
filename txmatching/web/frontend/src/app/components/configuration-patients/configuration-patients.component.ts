import { Component, ElementRef, Input, ViewChild } from '@angular/core';
import { FormControl } from '@angular/forms';
import { Patient, PatientList } from '@app/model/Patient';
import { Configuration } from '@app/model/Configuration';
import { Observable } from 'rxjs';
import { map, startWith } from 'rxjs/operators';
import { MatAutocompleteSelectedEvent } from '@angular/material/autocomplete';
import { patientFullTextSearch } from '@app/directives/validators/configForm.directive';

@Component({
  selector: 'app-configuration-patients',
  templateUrl: './configuration-patients.component.html',
  styleUrls: ['./configuration-patients.component.scss']
})
export class ConfigurationPatientsComponent {
  @Input() patients?: PatientList;
  @Input() configuration?: Configuration;

  @ViewChild('patientInput') patientInput?: ElementRef<HTMLInputElement>;

  public formControl = new FormControl('');
  public filteredPatients: Observable<Patient[]>;

  constructor() {
    this.filteredPatients = this.formControl.valueChanges.pipe(
      startWith(''),
      map((value: string | Patient) => {
        return typeof value === 'string' ? value : value.medical_id;
      }),
      map(name => name ? patientFullTextSearch(this.availablePatients, name) : this.availablePatients.slice())
    );
  }

  get allPatients(): Patient[] {
    return this.patients ? this.patients.recipients ?? [] : [];
  }

  get availablePatients(): Patient[] {
    return this.allPatients.filter(p => !this.selectedPatients.includes(p));
  }

  get selectedPatients(): Patient[] {
    if (!this.configuration) {
      return [];
    }
    const requiredPatientsIds = this.configuration.required_patient_db_ids;
    return this.allPatients.filter(p => requiredPatientsIds.includes(p.db_id));
  }

  public displayFn(user: Patient): string {
    return user && user.medical_id ? user.medical_id : '';
  }

  public add(event: MatAutocompleteSelectedEvent): void {
    const patient: Patient = event.option.value;
    this.configuration?.required_patient_db_ids.push(patient.db_id);

    // Reset input
    this.formControl.setValue('');
    if (this.patientInput) {
      this.patientInput.nativeElement.value = '';
    }
  }

  public remove(patient: Patient): void {
    if (!this.configuration) {
      return;
    }

    const index = this.configuration.required_patient_db_ids.indexOf(patient.db_id);

    if (index >= 0) {
      this.configuration.required_patient_db_ids.splice(index, 1);
    }
  }
}
