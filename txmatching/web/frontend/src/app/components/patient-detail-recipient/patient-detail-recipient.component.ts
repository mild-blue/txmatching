import { Component, Input, OnInit } from '@angular/core';
import { ListItemDetailAbstractComponent } from '@app/components/list-item/list-item.interface';
import { Antibody, PatientList, Recipient } from '@app/model/Patient';
import { FormControl, FormGroup } from '@angular/forms';
import { Observable } from 'rxjs';
import { PatientService } from '@app/services/patient/patient.service';
import { map, startWith } from 'rxjs/operators';
import { antibodiesFullTextSearch, countryFullTextSearch } from '@app/directives/validators/configForm.directive';

@Component({
  selector: 'app-patient-detail-recipient',
  templateUrl: './patient-detail-recipient.component.html',
  styleUrls: ['./patient-detail-recipient.component.scss']
})
export class PatientDetailRecipientComponent extends ListItemDetailAbstractComponent implements OnInit {

  @Input() patients?: PatientList;
  @Input() item?: Recipient;

  public form: FormGroup = new FormGroup({
    antigens: new FormControl(''),
    antibodies: new FormControl(''),
    require_better_match_in_compatibility_index: new FormControl(false),
    require_better_match_in_compatibility_index_or_blood_group: new FormControl(false),
    require_compatible_blood_group: new FormControl(false)
  });

  public allAntigensCodes: string[] = [];
  public filteredAntigensCodes: Observable<string[]>;

  public allAntibodies: Antibody[] = [];
  public filteredAntibodies: Observable<Antibody[]>;

  public enableSave: boolean = false;
  public loading: boolean = false;

  constructor(private _patientService: PatientService) {
    super(_patientService);

    this.filteredAntigensCodes = this.form.controls.antigens.valueChanges.pipe(
      startWith(undefined),
      map((code: string | null) => code ? countryFullTextSearch(this.availableAntigensCodes, code) : this.availableAntigensCodes.slice()));

    this.filteredAntibodies = this.form.controls.antibodies.valueChanges.pipe(
      startWith(''),
      map((value: string | Antibody) => {
        return typeof value === 'string' ? value : value.code;
      }),
      map(code => code ? antibodiesFullTextSearch(this.availableAntibodies, code) : this.availableAntibodies.slice())
    );
  }

  ngOnInit(): void {
    this._initAvailableAntigensCodes();
    this._initAvailableAntibodies();
  }

  get selectedAntigens(): string[] {
    return this.item ? this.item.parameters.hla_typing.codes : [];
  }

  get availableAntigensCodes(): string[] {
    return this.allAntigensCodes.filter(code => !this.selectedAntigens.includes(code));
  }

  get selectedAntibodies(): Antibody[] {
    return this.item ? this.item.hla_antibodies.antibodies_list : [];
  }

  get availableAntibodies(): Antibody[] {
    return this.allAntibodies.filter(code => !this.allAntibodies.includes(code));
  }

  public addAntigen(code: string): void {
    if (!this.item) {
      return;
    }

    this.item.parameters.hla_typing.codes.push(code);
    this.enableSave = true;
  }

  public removeAntigen(code: string): void {
    if (!this.item) {
      return;
    }

    const index = this.item.parameters.hla_typing.codes.indexOf(code);

    if (index >= 0) {
      this.item.parameters.hla_typing.codes.splice(index, 1);
      this.enableSave = true;
    }
  }

  public addAntibody(a: Antibody): void {
    if (!this.item) {
      return;
    }

    this.item.hla_antibodies.antibodies_list.push(a);
    this.enableSave = true;
  }

  public removeAntibody(a: Antibody): void {
    if (!this.item) {
      return;
    }

    const index = this.item.hla_antibodies.antibodies_list.indexOf(a);

    if (index >= 0) {
      this.item.hla_antibodies.antibodies_list.splice(index, 1);
      this.enableSave = true;
    }
  }

  public handleSubmit(): void {
    if (!this.item) {
      return;
    }

    console.log(this.item);
    this.loading = true;
    // this._patientService.saveDonor(this.item)
    // .then(() => this.loading = false)
    // .catch(() => this.loading = false);
  }

  public displayFn(a: Antibody): string {
    return a && a.code ? a.code : '';
  }

  private _initAvailableAntigensCodes(): void {
    if (!this.patients || !this.patients.recipients) {
      return;
    }

    const allCodes = [];
    for (const r of this.patients.recipients) {
      allCodes.push(...r.parameters.hla_typing.codes);
    }

    this.allAntigensCodes = [...new Set(allCodes)]; // only unique
  }

  private _initAvailableAntibodies(): void {
    if (!this.patients || !this.patients.recipients) {
      return;
    }

    const allCodes = [];
    for (const r of this.patients.recipients) {
      allCodes.push(...r.hla_antibodies.antibodies_list);
    }

    // todo
    // this.allAntibodies = [...new Set(allCodes)]; // only unique
  }

}
