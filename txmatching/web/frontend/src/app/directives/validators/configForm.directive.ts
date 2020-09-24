import { AbstractControl, FormControl, FormGroupDirective, NgForm, ValidatorFn } from '@angular/forms';
import { Patient } from '@app/model/Patient';
import { ErrorStateMatcher } from '@angular/material/core';

export function patientNameValidator(patients: Patient[]): ValidatorFn {
  return (control: AbstractControl): { [key: string]: any } | null => {
    const exists = patients.includes(control.value);
    return exists ? null : { invalidPatient: { value: control.value } };
  };
}

export function countryNameValidator(countries: string[]): ValidatorFn {
  return (control: AbstractControl): { [key: string]: any } | null => {
    const exists = countries.includes(control.value);
    return exists ? null : { invalidCountry: { value: control.value } };
  };
}

export function patientFullTextSearch(patients: Patient[], searchPhrase: string): Patient[] {
  const filterValue = searchPhrase.toLowerCase();
  const searchPattern = new RegExp(`(?=.*${filterValue})`);

  return patients.filter(patient => patient.medical_id.toLocaleLowerCase().match(searchPattern));
}

export function countryFullTextSearch(countries: string[], searchPhrase: string): string[] {
  const filterValue = searchPhrase.toLowerCase();
  const searchPattern = new RegExp(`(?=.*${filterValue})`);

  return countries.filter(c => c.toLocaleLowerCase().match(searchPattern));
}

export class ConfigErrorStateMatcher implements ErrorStateMatcher {
  isErrorState(control: FormControl | null, form: FormGroupDirective | NgForm | null): boolean {
    const isSubmitted = form && form.submitted;
    return !!(control && control.invalid && (((control.touched || control.dirty) && control.value) || isSubmitted));
  }
}
