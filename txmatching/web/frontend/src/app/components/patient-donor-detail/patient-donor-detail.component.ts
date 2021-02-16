import { Component, Input, OnInit } from '@angular/core';
import { ListItemDetailAbstractComponent } from '@app/components/list-item/list-item.interface';
import { FormControl } from '@angular/forms';
import { Observable } from 'rxjs';
import { map, startWith } from 'rxjs/operators';
import { hlaFullTextSearch } from '@app/directives/validators/configForm.directive';
import { PatientService } from '@app/services/patient/patient.service';
import { ENTER, SPACE } from '@angular/cdk/keycodes';
import { Donor } from '@app/model/Donor';
import { Antigen } from '@app/model/Hla';
import { PatientList } from '@app/model/PatientList';
import { TxmEvent } from '@app/model/Event';
import { LoggerService } from '@app/services/logger/logger.service';

@Component({
  selector: 'app-patient-detail-donor',
  templateUrl: './patient-donor-detail.component.html',
  styleUrls: ['./patient-donor-detail.component.scss']
})
export class PatientDonorDetailComponent extends ListItemDetailAbstractComponent implements OnInit {

  @Input() patients?: PatientList;
  @Input() item?: Donor;
  @Input() defaultTxmEvent?: TxmEvent;

  public inputControl: FormControl = new FormControl('');
  public allAntigens: Antigen[] = [];

  public filtered: Observable<Antigen[]>;
  public separatorKeysCodes: number[] = [ENTER, SPACE];

  public loading: boolean = false;
  public success: boolean = false;

  constructor(private _patientService: PatientService,
              private _logger: LoggerService) {
    super(_patientService);

    this.filtered = this.inputControl.valueChanges.pipe(
      startWith(''),
      map((value: string | Antigen) => {
        return !value || typeof value === 'string' ? value : value.code;
      }),
      map(code => code ? hlaFullTextSearch(this.available, code) : this.available.slice())
    );
  }

  ngOnInit(): void {
    this._initAvailableCodes();
  }

  get selected(): Antigen[] {
    return this.item ? this.item.parameters.hla_typing.hla_types_list : [];
  }

  get available(): Antigen[] {
    const selectedAntigensCodes = [...new Set(this.selected.map(antigen => antigen.code))];
    return this.allAntigens.filter(a => !selectedAntigensCodes.includes(a.code));
  }

  public setActiveValue(value: boolean): void {
    if(this.item) this.item.active = value;
  }

  public addNewAntigen(code: string, control: HTMLInputElement): void {
    if(!this.item) {
      this._logger.error(`addNewAntigen failed because item not set`);
      return;
    }
    if(!code.length) return;

    const formattedCode = code.trim().toUpperCase();
    this.item.parameters.hla_typing.hla_types_list.push({ code: formattedCode, raw_code: formattedCode });

    // reset input
    this.inputControl.reset();
    control.value = '';
  }

  public addAntigen(a: Antigen, control: HTMLInputElement): void {
    if(!this.item) {
      this._logger.error(`addAntigen failed because item not set`);
      return;
    }
    if (!a) return;

    this.item.parameters.hla_typing.hla_types_list.push(a);

    // reset input
    this.inputControl.reset();
    control.value = '';
  }

  public remove(code: Antigen): void {
    if(!this.item) {
      this._logger.error(`remove failed because item not set`);
      return;
    }

    const index = this.item.parameters.hla_typing.hla_types_list.indexOf(code);

    if (index >= 0) {
      this.item.parameters.hla_typing.hla_types_list.splice(index, 1);
    }
  }

  public handleSave(): void {
    if(!this.item) {
      this._logger.error(`handleSave failed because item not set`);
      return;
    }
    if(!this.defaultTxmEvent) {
      this._logger.error(`handleSave failed because defaultTxmEvent not set`);
      return;
    }

    this.loading = true;
    this.success = false;
    this._patientService.saveDonor(this.defaultTxmEvent.id, this.item)
    .then(() => {
      this.loading = false;
      this.success = true;
    })
    .catch(() => this.loading = false);
  }

  private _initAvailableCodes(): void {
    if(!this.patients?.donors) {
      this._logger.error(`initAvailableCodes failed because donors not set`);
      return;
    }

    const allAntigens = [];
    for (const d of this.patients.donors) {
      allAntigens.push(...d.parameters.hla_typing.hla_types_list);
    }

    this.allAntigens = [...new Set(allAntigens.map(a => a.code))].map(code => {
      return { code, raw_code: code ?? '' };
    }); // only unique
  }
}
