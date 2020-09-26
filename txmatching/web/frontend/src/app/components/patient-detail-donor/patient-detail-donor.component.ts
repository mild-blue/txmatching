import { Component, Input, OnInit } from '@angular/core';
import { ListItemDetailAbstractComponent } from '@app/components/list-item/list-item.interface';
import { FormControl } from '@angular/forms';
import { Observable } from 'rxjs';
import { map, startWith } from 'rxjs/operators';
import { countryFullTextSearch } from '@app/directives/validators/configForm.directive';
import { Donor, PatientList } from '@app/model/Patient';

@Component({
  selector: 'app-patient-detail-donor',
  templateUrl: './patient-detail-donor.component.html',
  styleUrls: ['./patient-detail-donor.component.scss']
})
export class PatientDetailDonorComponent extends ListItemDetailAbstractComponent implements OnInit {

  @Input() patients?: PatientList;
  @Input() item?: Donor;

  public inputControl: FormControl = new FormControl('');

  public allCodes: string[] = [];
  public filteredCodes: Observable<string[]>;

  constructor() {
    super();

    this.filteredCodes = this.inputControl.valueChanges.pipe(
      startWith(undefined),
      map((code: string | null) => code ? countryFullTextSearch(this.availableCodes, code) : this.availableCodes.slice()));
  }

  ngOnInit(): void {
    this._initAvailableCodes();
  }

  get selectedCodes(): string[] {
    return this.item ? this.item.parameters.hla_typing.codes : [];
  }

  get availableCodes(): string[] {
    return this.allCodes.filter(code => !this.selectedCodes.includes(code));
  }

  public add(code: string): void {
    if (!this.item) {
      return;
    }

    this.item.parameters.hla_typing.codes.push(code);
  }

  public remove(code: string): void {
    if (!this.item) {
      return;
    }

    const index = this.item.parameters.hla_typing.codes.indexOf(code);

    if (index >= 0) {
      this.item.parameters.hla_typing.codes.splice(index, 1);
    }
  }

  private _initAvailableCodes(): void {
    console.log('init av codes', this.patients);
    if (!this.patients || !this.patients.donors) {
      return;
    }

    const allCodes = [];
    for (const d of this.patients.donors) {
      allCodes.push(...d.parameters.hla_typing.codes);
    }

    this.allCodes = [...new Set(allCodes)]; // only unique
  }
}
