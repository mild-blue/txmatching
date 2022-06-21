import { AbstractControl, FormControl, FormGroupDirective, NgForm, ValidatorFn, NgModel, FormGroup } from '@angular/forms';
import { Patient } from '@app/model/Patient';
import { ErrorStateMatcher } from '@angular/material/core';
import { Hla } from '@app/model/Hla';
import { ENTER, SPACE } from '@angular/cdk/keycodes';
import { PatientEditable } from '@app/model/PatientEditable';

export const separatorKeysCodes: number[] = [ENTER, SPACE];

// custom validator to check that two fields match
export function mustMatchValidator(controlName: string, matchingControlName: string) {
  return (formGroup: FormGroup) => {
    const control = formGroup.controls[controlName];
    const matchingControl = formGroup.controls[matchingControlName];

    if (matchingControl.errors && !matchingControl.errors.mustMatch) {
      // return if another validator has already found an error on the matchingControl
      return;
    }

    // set error on matchingControl if validation fails
    if (control.value !== matchingControl.value) {
      matchingControl.setErrors({ mustMatch: true });
    } else {
      matchingControl.setErrors(null);
    }
  };
}

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

  return patients.filter(patient => patient.medicalId.toLocaleLowerCase().match(searchPattern));
}

export function hlaFullTextSearch(antibodies: Hla[], searchPhrase: string): Hla[] {
  const filterValue = searchPhrase.toLowerCase();
  const searchPattern = new RegExp(`(?=.*${filterValue})`);

  return antibodies.filter(a => a.code?.displayCode.toLocaleLowerCase().match(searchPattern));
}

export function countryFullTextSearch(countries: string[], searchPhrase: string): string[] {
  const filterValue = searchPhrase.toLowerCase();
  const searchPattern = new RegExp(`(?=.*${filterValue})`);

  return countries.filter(c => c.toLocaleLowerCase().match(searchPattern));
}

export function formatYearOfBirthForPatient(inputValue: NgModel, patient: PatientEditable): void {
  formatNumberForPatient(inputValue, patient);
}

export function formatNumberForPatient(
  inputValue: NgModel, patient: PatientEditable): number | undefined {
  let newValue: number | undefined;
  if (!inputValue.value) {
    newValue = undefined;
  } else {
    newValue = +inputValue.value;
  }

  switch (inputValue.name) {
    case 'height':
      patient.height = newValue;
      break;
    case 'weight':
      patient.weight = newValue;
      break;
    case 'yearOfBirth':
      patient.yearOfBirth = newValue;
      break;
  }

  inputValue.update.emit(newValue);

  return newValue;
}

export class ControlErrorStateMatcher implements ErrorStateMatcher {
  isErrorState(control: FormControl | null, form: FormGroupDirective | NgForm | null): boolean {
    const isSubmitted = form && form.submitted;
    return !!(control && control.invalid && (((control.touched || control.dirty) && control.value) || isSubmitted));
  }
}
