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

export class ConfigErrorStateMatcher implements ErrorStateMatcher {
  isErrorState(control: FormControl | null, form: FormGroupDirective | NgForm | null): boolean {
    const isSubmitted = form && form.submitted;
    return !!(control && control.invalid && (((control.touched || control.dirty) && control.value) || isSubmitted));
  }
}
