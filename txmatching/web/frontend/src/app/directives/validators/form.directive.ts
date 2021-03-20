import { AbstractControl, FormControl, FormGroupDirective, NgForm, ValidatorFn } from '@angular/forms';
import { Patient } from '@app/model/Patient';
import { ErrorStateMatcher } from '@angular/material/core';
import { Hla } from '@app/model/Hla';
import { ENTER, SPACE } from '@angular/cdk/keycodes';

export const separatorKeysCodes: number[] = [ENTER, SPACE];

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

export class ControlErrorStateMatcher implements ErrorStateMatcher {
  isErrorState(control: FormControl | null, form: FormGroupDirective | NgForm | null): boolean {
    const isSubmitted = form && form.submitted;
    return !!(control && control.invalid && (((control.touched || control.dirty) && control.value) || isSubmitted));
  }
}
