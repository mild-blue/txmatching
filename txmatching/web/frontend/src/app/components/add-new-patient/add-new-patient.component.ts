import { Component, OnInit } from '@angular/core';
import { Country } from '@app/model/Country';
import { FormControl, FormGroup } from '@angular/forms';
import { map, startWith } from 'rxjs/operators';
import { countryFullTextSearch, countryNameValidator, separatorKeysCodes } from '@app/directives/validators/form.directive';
import { Observable } from 'rxjs';
import { AbstractFormHandlerComponent } from '@app/components/abstract-form-handler/abstract-form-handler.component';
import { BloodGroup, DonorNew, DonorType, Sex } from '@app/model';

@Component({
  selector: 'app-add-new-patient',
  templateUrl: './add-new-patient.component.html',
  styleUrls: ['./add-new-patient.component.scss']
})
export class AddNewPatientComponent extends AbstractFormHandlerComponent implements OnInit {

  public form: FormGroup = new FormGroup({
    country: new FormControl('')
  });

  public allCountries: string[] = Object.keys(Country).map(key => `${Country[key as Country]}`);
  public allDonorTypes: DonorType[] = Object.keys(DonorType).map(key => DonorType[key as DonorType]);
  // @ts-ignore
  public allBloodGroups: string[] = Object.keys(BloodGroup).map(key => `${BloodGroup[key as BloodGroup]}`);
  public allSexes: string[] = Object.keys(Sex).map(key => `${Sex[key as Sex]}`);

  public filteredCountries: Observable<string[]>;
  public separatorKeysCodes: number[] = separatorKeysCodes;

  public donor: DonorNew = new DonorNew();
  public loading: boolean = false;
  public success: boolean = false;

  constructor() {
    super();

    // Country fulltext search
    this.filteredCountries = this.form.controls.country?.valueChanges.pipe(
      startWith(undefined),
      map((country: string | null) => country ? countryFullTextSearch(this.allCountries, country) : this.allCountries.slice()));
  }

  ngOnInit() {
    // Allow only existing countries
    this.form.controls.country?.setValidators(countryNameValidator(this.allCountries));
  }

  get selectedCountry(): string {
    return this.form.controls.country?.value ?? '';
  }

  public addAntigen(donor: DonorNew, code: string, control: HTMLInputElement): void {
    if (!code) {
      return;
    }

    donor.addAntigen(code);

    // Reset input
    control.value = '';
  }

  public handleSubmit() {
    console.log(this.form.valid, this.donor);
  }
}
