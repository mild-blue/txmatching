import { Component, Input } from '@angular/core';
import { PatientList } from '@app/model/Patient';
import { Configuration, CountryCombination } from '@app/model/Configuration';
import { FormControl } from '@angular/forms';
import { Observable } from 'rxjs';
import { map, startWith } from 'rxjs/operators';

@Component({
  selector: 'app-configuration-countries',
  templateUrl: './configuration-countries.component.html',
  styleUrls: ['./configuration-countries.component.scss']
})
export class ConfigurationCountriesComponent {
  @Input() patients?: PatientList;
  @Input() configuration?: Configuration;

  public donorFormControl = new FormControl('');
  public recipientFormControl = new FormControl('');

  public filteredDonorCountries: Observable<string[]>;
  public filteredRecipientCountries: Observable<string[]>;

  private _donorCountries: string[] = [];
  private _recipientCountries: string[] = [];

  constructor() {
    this.filteredDonorCountries = this.donorFormControl.valueChanges.pipe(
      startWith(null),
      map((country: string | null) => country ? this._filter(this.donorCountries, country) : this.donorCountries.slice()));

    this.filteredRecipientCountries = this.donorFormControl.valueChanges.pipe(
      startWith(null),
      map((country: string | null) => country ? this._filter(this.recipientCountries, country) : this.recipientCountries.slice()));
  }

  get donorCountries(): string[] {
    if (!this.patients || !this.patients.donors) {
      return [];
    }

    if (!this._donorCountries.length) {
      const countries = this.patients.donors.map(p => p.parameters.country_code);
      this._donorCountries = [...new Set(countries)]; // only unique
    }

    return this._donorCountries;
  }

  get recipientCountries(): string[] {
    if (!this.patients || !this.patients.recipients) {
      return [];
    }

    if (!this._recipientCountries.length) {
      const countries = this.patients.recipients.map(p => p.parameters.country_code);
      this._recipientCountries = [...new Set(countries)]; // only unique
    }

    return this._recipientCountries;
  }

  get selectedCombinations(): CountryCombination[] {
    return this.configuration ? this.configuration.forbidden_country_combinations : [];
  }

  public setDonorCountry(c: CountryCombination, country: string, input: HTMLInputElement): void {
    c.donor_country = country;

    // Reset input
    this.donorFormControl.setValue('');
    input.value = '';
  }

  public setRecipientCountry(c: CountryCombination, country: string, input: HTMLInputElement): void {
    c.recipient_country = country;

    // Reset input
    this.recipientFormControl.setValue('');
    input.value = '';
  }

  public addCombination(): void {
    this.configuration?.forbidden_country_combinations.push({
      donor_country: '',
      recipient_country: ''
    });
  }

  public removeCombination(c: CountryCombination): void {
    if (!this.configuration) {
      return;
    }
    const countries = this.configuration.forbidden_country_combinations;
    const index = countries.indexOf(c);

    if (index >= 0) {
      countries.splice(index, 1);
    }
  }

  // filter while typing
  private _filter(list: string[], value: string): string[] {
    const filterValue = value.toLowerCase();
    return list.filter(c => c.toLowerCase().indexOf(filterValue) === 0);
  }
}
