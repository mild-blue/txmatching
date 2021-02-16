import { Component, Input, OnInit } from '@angular/core';
import { PatientEditable } from '@app/model/PatientEditable';
import { Country } from '@app/model/Country';
import { FormControl, FormGroup } from '@angular/forms';
import { map, startWith } from 'rxjs/operators';
import { countryFullTextSearch, countryNameValidator, separatorKeysCodes } from '@app/directives/validators/form.directive';
import { Observable } from 'rxjs';
import { AbstractFormHandlerComponent } from '@app/components/abstract-form-handler/abstract-form-handler.component';

@Component({
  selector: 'app-country-setting',
  templateUrl: './country-setting.component.html',
  styleUrls: ['./country-setting.component.scss']
})
export class CountrySettingComponent extends AbstractFormHandlerComponent implements OnInit {

  @Input() patient?: PatientEditable;

  public allCountries: string[] = Object.values(Country);
  public filteredCountries: Observable<string[]>;
  public separatorKeysCodes: number[] = separatorKeysCodes;

  public form: FormGroup = new FormGroup({
    country: new FormControl('')
  });

  constructor() {
    super();

    // Country fulltext search
    this.filteredCountries = this.form.controls.country?.valueChanges.pipe(
      startWith(undefined),
      map((country: string | null) => country ? countryFullTextSearch(this.allCountries, country) : this.allCountries.slice()));
  }

  ngOnInit(): void {
    // Allow only existing countries
    this.form.controls.country?.setValidators(countryNameValidator(this.allCountries));

    // Set value to patient country
    if (this.patient) {
      this.form.controls.country?.setValue(this.patient.country.valueOf());
    }
  }

  get selectedCountry(): string {
    return this.form.controls.country?.value ?? '';
  }

  public handleCountrySelect(control: HTMLInputElement): void {

    // Set country to patient
    if (this.patient) {
      this.patient.country = this.selectedCountry as Country;
    }

    // Disable control, so multiple countries cannot be selected
    this.handleSelect(control);
  }
}
