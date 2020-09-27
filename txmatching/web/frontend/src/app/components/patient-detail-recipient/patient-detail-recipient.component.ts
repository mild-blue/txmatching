import { Component, Input, OnInit } from '@angular/core';
import { ListItemDetailAbstractComponent } from '@app/components/list-item/list-item.interface';
import { PatientList, Recipient } from '@app/model/Patient';
import { FormControl, FormGroup } from '@angular/forms';
import { Observable } from 'rxjs';
import { PatientService } from '@app/services/patient/patient.service';
import { map, startWith } from 'rxjs/operators';
import { countryFullTextSearch } from '@app/directives/validators/configForm.directive';
import { ENTER } from '@angular/cdk/keycodes';

@Component({
  selector: 'app-patient-detail-recipient',
  templateUrl: './patient-detail-recipient.component.html',
  styleUrls: ['./patient-detail-recipient.component.scss']
})
export class PatientDetailRecipientComponent extends ListItemDetailAbstractComponent implements OnInit {

  @Input() patients?: PatientList;
  @Input() item?: Recipient;

  public success: boolean = false;

  public form: FormGroup = new FormGroup({
    antigens: new FormControl(''),
    require_better_match_in_compatibility_index: new FormControl(false),
    require_better_match_in_compatibility_index_or_blood_group: new FormControl(false),
    require_compatible_blood_group: new FormControl(false)
  });

  public allAntigensCodes: string[] = [];
  public filteredAntigensCodes: Observable<string[]>;

  public loading: boolean = false;

  public separatorKeysCodes: number[] = [ENTER];

  constructor(private _patientService: PatientService) {
    super(_patientService);

    this.filteredAntigensCodes = this.form.controls.antigens.valueChanges.pipe(
      startWith(undefined),
      map((code: string | null) => code ? countryFullTextSearch(this.availableAntigensCodes, code) : this.availableAntigensCodes.slice()));
  }

  ngOnInit(): void {
    this._initAntigensCodes();
  }

  get selectedAntigens(): string[] {
    return this.item ? this.item.parameters.hla_typing.codes : [];
  }

  get availableAntigensCodes(): string[] {
    return this.allAntigensCodes.filter(code => !this.selectedAntigens.includes(code));
  }

  public addAntigen(code: string, control: HTMLInputElement): void {
    if (!this.item || !code.length) {
      return;
    }

    const formattedCode = code.trim().toUpperCase();
    this.item.parameters.hla_typing.codes.push(formattedCode);

    // reset input
    this.form.controls.antigens.reset();
    control.value = '';
  }

  public removeAntigen(code: string): void {
    if (!this.item) {
      return;
    }

    const index = this.item.parameters.hla_typing.codes.indexOf(code);

    if (index >= 0) {
      this.item.parameters.hla_typing.codes.splice(index, 1);
    }
  }

  public setCheckBoxValue(key: string, value: boolean): void {
    if (this.item && this.item.recipient_requirements[key] !== undefined) {
      this.item.recipient_requirements[key] = value;
    }
  }

  public handleSave(): void {
    if (!this.item) {
      return;
    }

    this.loading = true;
    this.success = false;
    this._patientService.saveRecipient(this.item)
    .then(() => {
      this.loading = false;
      this.success = true;
    })
    .catch(() => this.loading = false);
  }

  private _initAntigensCodes(): void {
    if (!this.patients || !this.patients.recipients) {
      return;
    }

    const allAntigens = [];
    for (const r of this.patients.recipients) {
      allAntigens.push(...r.parameters.hla_typing.codes);
    }

    this.allAntigensCodes = [...new Set(allAntigens)]; // only unique
  }
}
