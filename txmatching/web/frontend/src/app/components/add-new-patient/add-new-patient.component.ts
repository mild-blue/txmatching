import { Component, EventEmitter, Input, OnInit, Output } from '@angular/core';
import { Country } from '@app/model/Country';
import { FormControl, FormGroup } from '@angular/forms';
import { map, startWith } from 'rxjs/operators';
import { countryFullTextSearch, countryNameValidator, separatorKeysCodes } from '@app/directives/validators/form.directive';
import { Observable } from 'rxjs';
import { AbstractFormHandlerComponent } from '@app/components/abstract-form-handler/abstract-form-handler.component';
import { BloodGroup, DonorType, Sex } from '@app/model';
import { DonorEditable } from '@app/model/DonorEditable';
import { RecipientEditable } from '@app/model/RecipientEditable';
import { PatientService } from '@app/services/patient/patient.service';
import { TxmEvent } from '@app/model/Event';

@Component({
  selector: 'app-add-new-patient',
  templateUrl: './add-new-patient.component.html',
  styleUrls: ['./add-new-patient.component.scss']
})
export class AddNewPatientComponent extends AbstractFormHandlerComponent implements OnInit {

  @Input() defaultTxmEvent?: TxmEvent;
  @Output() patientsAdded: EventEmitter<void> = new EventEmitter<void>();

  public form: FormGroup = new FormGroup({
    country: new FormControl('')
  });

  public allCountries: string[] = Object.values(Country);
  public allDonorTypes: DonorType[] = Object.values(DonorType);
  public allBloodGroups: BloodGroup[] = Object.values(BloodGroup);
  public allSexes: Sex[] = Object.values(Sex);

  public DonorType: typeof DonorType = DonorType;

  public filteredCountries: Observable<string[]>;
  public separatorKeysCodes: number[] = separatorKeysCodes;

  public donor: DonorEditable = new DonorEditable();
  public recipient: RecipientEditable = new RecipientEditable();

  public loading: boolean = false;
  public success: boolean = false;

  constructor(private _patientService: PatientService) {
    super();

    // Country fulltext search
    this.filteredCountries = this.form.controls.country?.valueChanges.pipe(
      startWith(undefined),
      map((country: string | null) => country ? countryFullTextSearch(this.allCountries, country) : this.allCountries.slice()));
  }

  ngOnInit() {
    console.log(Object.values(DonorType));
    // Allow only existing countries
    this.form.controls.country?.setValidators(countryNameValidator(this.allCountries));
  }

  get selectedCountry(): string {
    return this.form.controls.country?.value ?? '';
  }

  public addAntigen(donor: DonorEditable, code: string, control: HTMLInputElement): void {
    if (!code) {
      return;
    }

    donor.addAntigen(code);

    // Reset input
    control.value = '';
  }

  public handleSubmit() {

    console.log(this.form.valid, this.donor, this.recipient);
    if (this.form.invalid || !this.defaultTxmEvent) {
      return;
    }

    const country = this.form.get('country')?.value;
    const recipient = this.donor.type === DonorType.DONOR.valueOf() ? this.recipient : undefined;

    this._patientService.addNewPair(this.defaultTxmEvent.id, country, this.donor, recipient)
    .then(() => this.patientsAdded.emit());
  }
}
