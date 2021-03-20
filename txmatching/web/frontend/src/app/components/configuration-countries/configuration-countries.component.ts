import { Component, ElementRef, Input, ViewChild } from '@angular/core';
import { Configuration, CountryCombination } from '@app/model/Configuration';
import { FormControl, FormGroup, NgForm, Validators } from '@angular/forms';
import { Observable } from 'rxjs';
import { map, startWith } from 'rxjs/operators';
import { countryFullTextSearch, countryNameValidator } from '@app/directives/validators/form.directive';
import { PatientList } from '@app/model/PatientList';
import { AbstractFormHandlerComponent } from '@app/components/abstract-form-handler/abstract-form-handler.component';

@Component({
  selector: 'app-configuration-countries',
  templateUrl: './configuration-countries.component.html',
  styleUrls: ['./configuration-countries.component.scss']
})
export class ConfigurationCountriesComponent extends AbstractFormHandlerComponent {
  private _donorCountries: string[] = [];
  private _recipientCountries: string[] = [];

  @Input() patients?: PatientList;
  @Input() configuration?: Configuration;

  @ViewChild('viewForm') viewForm?: NgForm;
  @ViewChild('viewDonorCountry') viewDonorCountry?: ElementRef<HTMLInputElement>;
  @ViewChild('viewRecipientCountry') viewRecipientCountry?: ElementRef<HTMLInputElement>;

  public form: FormGroup = new FormGroup({
    donorCountry: new FormControl('', Validators.required),
    recipientCountry: new FormControl('', Validators.required)
  });

  public filteredDonorCountries: Observable<string[]>;
  public filteredRecipientCountries: Observable<string[]>;

  constructor() {
    super();

    this.filteredDonorCountries = this.form.controls.donorCountry?.valueChanges.pipe(
      startWith(undefined),
      map((country: string | null) => country ? countryFullTextSearch(this.donorCountries, country) : this.donorCountries.slice()));

    this.filteredRecipientCountries = this.form.controls.recipientCountry?.valueChanges.pipe(
      startWith(undefined),
      map((country: string | null) => country ? countryFullTextSearch(this.recipientCountries, country) : this.recipientCountries.slice()));
  }

  ngOnInit() {
    this.form.controls.donorCountry.setValidators(countryNameValidator(this.donorCountries));
    this.form.controls.recipientCountry.setValidators(countryNameValidator(this.recipientCountries));
  }

  get donorCountries(): string[] {
    if (!this.patients?.donors) {
      return [];
    }

    if (!this._donorCountries.length) {
      const countries = this.patients.donors.map(p => p.parameters.countryCode);
      this._donorCountries = [...new Set(countries)]; // only unique
    }

    return this._donorCountries;
  }

  get recipientCountries(): string[] {
    if (!this.patients?.recipients) {
      return [];
    }

    if (!this._recipientCountries.length) {
      const countries = this.patients.recipients.map(p => p.parameters.countryCode);
      this._recipientCountries = [...new Set(countries)]; // only unique
    }

    return this._recipientCountries;
  }

  get selectedCombinations(): CountryCombination[] {
    return this.configuration?.forbidden_country_combinations ?? [];
  }

  get donorCountry(): string {
    return this.form.controls.donorCountry.value ?? '';
  }

  get recipientCountry(): string {
    return this.form.controls.recipientCountry.value ?? '';
  }

  public addCombination(): void {
    if (this.form.pristine || this.form.untouched || !this.form.valid) {
      return;
    }

    const { donorCountry, recipientCountry } = this.form.value;

    this.configuration?.forbidden_country_combinations.push({
      donor_country: donorCountry,
      recipient_country: recipientCountry
    });

    // reset form
    this.form.reset();
    this.viewForm?.resetForm('');

    // enable inputs
    if (this.viewDonorCountry) {
      this.viewDonorCountry.nativeElement.disabled = false;
    }
    if (this.viewRecipientCountry) {
      this.viewRecipientCountry.nativeElement.disabled = false;
    }
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
}
