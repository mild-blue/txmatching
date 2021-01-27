import { Component, Input, OnInit } from '@angular/core';
import { ListItemDetailAbstractComponent } from '@app/components/list-item/list-item.interface';
import { FormControl, FormGroup } from '@angular/forms';
import { Observable } from 'rxjs';
import { PatientService } from '@app/services/patient/patient.service';
import { map, startWith } from 'rxjs/operators';
import { hlaFullTextSearch } from '@app/directives/validators/configForm.directive';
import { ENTER, SPACE } from '@angular/cdk/keycodes';
import { Recipient } from '@app/model/Recipient';
import { Antibody, Antigen } from '@app/model/Hla';
import { PatientList } from '@app/model/PatientList';

@Component({
  selector: 'app-patient-detail-recipient',
  templateUrl: './patient-recipient-detail.component.html',
  styleUrls: ['./patient-recipient-detail.component.scss']
})
export class PatientRecipientDetailComponent extends ListItemDetailAbstractComponent implements OnInit {

  @Input() patients?: PatientList;
  @Input() item?: Recipient;

  public success: boolean = false;

  public form: FormGroup = new FormGroup({
    antigens: new FormControl('')
  });

  public allAntigens: Antigen[] = [];
  public filteredAntigensCodes: Observable<Antigen[]>;

  public loading: boolean = false;

  public separatorKeysCodes: number[] = [ENTER, SPACE];

  constructor(private _patientService: PatientService) {
    super(_patientService);

    this.filteredAntigensCodes = this.form.controls.antigens.valueChanges.pipe(
      startWith(''),
      map((value: string | Antigen) => {
        return !value || typeof value === 'string' ? value : value.code;
      }),
      map(code => code ? hlaFullTextSearch(this.availableAntigens, code) : this.availableAntigens.slice())
    );
  }

  ngOnInit(): void {
    this._initAntigensCodes();
  }

  get selectedAntigens(): Antigen[] {
    return this.item ? this.item.parameters.hla_typing.hla_types_list : [];
  }

  get availableAntigens(): Antigen[] {
    const selectedAntigensCodes = [...new Set(this.selectedAntigens.map(antigen => antigen.code))];
    return this.allAntigens.filter(a => !selectedAntigensCodes.includes(a.code));
  }

  public addAntigen(a: Antigen, control: HTMLInputElement): void {
    if (!this.item || !a) {
      return;
    }

    this.item.parameters.hla_typing.hla_types_list.push(a);

    // reset input
    this.form.controls.antigens.reset();
    control.value = '';
  }

  public addNewAntigen(code: string, control: HTMLInputElement): void {
    if (!this.item || !code) {
      return;
    }

    const formattedCode = code.trim().toUpperCase();
    this.item.parameters.hla_typing.hla_types_list.push({ code: formattedCode, raw_code: formattedCode });

    // reset input
    this.form.controls.antigens.reset();
    control.value = '';
  }

  public removeAntigen(antigen: Antigen): void {
    if (!this.item) {
      return;
    }

    const index = this.item.parameters.hla_typing.hla_types_list.indexOf(antigen);

    if (index >= 0) {
      this.item.parameters.hla_typing.hla_types_list.splice(index, 1);
    }
  }

  public setCheckBoxValue(key: string, value: boolean): void {
    if (this.item?.recipient_requirements && this.item.recipient_requirements[key] !== undefined) {
      this.item.recipient_requirements[key] = value;
    }
  }

  public handleNewAntibody(antibody: Antibody): void {
    if (!this.item) {
      return;
    }
    this.handleSave([antibody]);
  }

  public handleSave(newAntibodies?: Antibody[]): void {
    if (!this.item) {
      return;
    }

    this.loading = true;
    this.success = false;
    const oldAntibodies = this.item.hla_antibodies.hla_antibodies_list;
    const antibodies = newAntibodies ? [...oldAntibodies, ...newAntibodies] : oldAntibodies;
    this._patientService.saveRecipient(this.item, antibodies)
    .then((recipient) => {
      this.success = true;
      this.item = recipient;
    })
    .finally(() => this.loading = false);
  }

  private _initAntigensCodes(): void {
    if (!this.patients?.recipients) {
      return;
    }

    const allAntigens = [];
    for (const r of this.patients.recipients) {
      allAntigens.push(...r.parameters.hla_typing.hla_types_list);
    }

    this.allAntigens = [...new Set(allAntigens.map(a => a.code))].map(code => {
      return { code, raw_code: code ?? '' };
    }); // only unique
  }
}
