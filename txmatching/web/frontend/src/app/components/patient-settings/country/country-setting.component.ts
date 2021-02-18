import { Component, Input, KeyValueDiffer, KeyValueDiffers, OnInit } from '@angular/core';
import { PatientEditable } from '@app/model/PatientEditable';
import { FormControl } from '@angular/forms';
import { map, startWith } from 'rxjs/operators';
import { countryFullTextSearch, countryNameValidator, separatorKeysCodes } from '@app/directives/validators/form.directive';
import { Observable } from 'rxjs';
import { AbstractFormHandlerComponent } from '@app/components/abstract-form-handler/abstract-form-handler.component';
import { CountryCodeGenerated } from '@app/generated';

@Component({
  selector: 'app-country-setting',
  templateUrl: './country-setting.component.html',
  styleUrls: ['./country-setting.component.scss']
})
export class CountrySettingComponent extends AbstractFormHandlerComponent implements OnInit {

  private _patientDiffer?: KeyValueDiffer<string, unknown>;

  @Input() patient?: PatientEditable;

  public allCountries: string[] = Object.values(CountryCodeGenerated);
  public filteredCountries: Observable<string[]>;
  public separatorKeysCodes: number[] = separatorKeysCodes;
  public countryControl: FormControl = new FormControl('');

  constructor(private _differs: KeyValueDiffers) {
    super();

    // Country fulltext search
    this.filteredCountries = this.countryControl.valueChanges.pipe(
      startWith(undefined),
      map((country: string | null) => country ? countryFullTextSearch(this.allCountries, country) : this.allCountries.slice()));
  }

  ngOnInit(): void {
    // Allow only existing countries
    this.countryControl.setValidators(countryNameValidator(this.allCountries));

    // Set value to patient country
    if (this.patient) {
      this.countryControl.setValue(this.patient.country?.valueOf());

      // Detect country change in patient
      this._patientDiffer = this._differs.find(this.patient).create();
    }
  }

  ngDoCheck(): void {
    const patientChanges = this._patientDiffer?.diff((this.patient as unknown) as Map<string, unknown>);
    patientChanges?.forEachChangedItem((record) => {
      if (record.key === 'country') {
        this.countryControl.setValue(record.currentValue);
      }
    });
  }

  get selectedCountryValue(): string {
    return this.countryControl.value ?? '';
  }

  public handleCountrySelect(control: HTMLInputElement): void {
    const country: CountryCodeGenerated = this.selectedCountryValue as CountryCodeGenerated;

    // Set country to patient
    this.patient?.setCountry(country);

    // Disable control, so multiple countries cannot be selected
    this.handleSelect(control);
  }

  handleCountryRemove(control: HTMLInputElement) {
    this.countryControl.setValue('');
    this.patient?.setCountry(undefined);
    control.disabled = false;
  }
}
