import { Component, Input } from '@angular/core';
import { PatientList } from '@app/model/Patient';
import { Configuration, CountryCombination } from '@app/model/Configuration';
import { FormControl, FormGroup } from '@angular/forms';
import { Observable } from 'rxjs';
import { map, startWith } from 'rxjs/operators';

@Component({
  selector: 'app-configuration-countries',
  templateUrl: './configuration-countries.component.html',
  styleUrls: ['./configuration-countries.component.scss']
})
export class ConfigurationCountriesComponent {
  private _donorCountries: string[] = [];
  private _recipientCountries: string[] = [];

  @Input() patients?: PatientList;
  @Input() configuration?: Configuration;

  public form: FormGroup = new FormGroup({
    donorCountry: new FormControl(''),
    recipientCountry: new FormControl('')
  });

  public filteredDonorCountries: Observable<string[]>;
  public filteredRecipientCountries: Observable<string[]>;

  constructor() {
    this.filteredDonorCountries = this.form.controls.donorCountry?.valueChanges.pipe(
      startWith(undefined),
      map((country: string | null) => country ? this._filter(this.donorCountries, country) : this.donorCountries.slice()));

    this.filteredRecipientCountries = this.form.controls.recipientCountry?.valueChanges.pipe(
      startWith(undefined),
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

  public addCombination(): void {
    const { donorCountry, recipientCountry } = this.form.value;

    this.configuration?.forbidden_country_combinations.push({
      donor_country: donorCountry,
      recipient_country: recipientCountry
    });

    this.form.reset();
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
