import { Component, EventEmitter, Input, OnInit, Output, ViewChild } from '@angular/core';
import { FormControl, FormGroup, NgForm, Validators } from '@angular/forms';
import { Observable } from 'rxjs';
import { ENTER } from '@angular/cdk/keycodes';
import { ConfigErrorStateMatcher, hlaFullTextSearch } from '@app/directives/validators/configForm.directive';
import { map, startWith } from 'rxjs/operators';
import { PatientList } from '@app/model/PatientList';
import { Recipient } from '@app/model/Recipient';
import { Antibody, Hla } from '@app/model/Hla';

@Component({
  selector: 'app-antibodies',
  templateUrl: './antibodies.component.html',
  styleUrls: ['./antibodies.component.scss']
})
export class AntibodiesComponent implements OnInit {

  @Input() patients?: PatientList;
  @Input() recipient?: Recipient;
  @Output() antibodyAdded: EventEmitter<Antibody> = new EventEmitter<Antibody>();

  @ViewChild('viewForm') viewForm?: NgForm;

  public form: FormGroup = new FormGroup({
    antibody: new FormControl('', Validators.required),
    mfi: new FormControl('', Validators.required)
  });

  public allAntibodies: Antibody[] = [];
  public filteredAntibodies: Observable<Hla[]>;

  public separatorKeysCodes: number[] = [ENTER];
  public errorMatcher = new ConfigErrorStateMatcher();

  public antibodyValue: string = '';

  constructor() {
    this.filteredAntibodies = this.form.controls.antibody.valueChanges.pipe(
      startWith(''),
      map((value: string | Antibody) => {
        return !value || typeof value === 'string' ? value : value.code;
      }),
      map(code => code ? hlaFullTextSearch(this.availableAntibodies, code) : this.availableAntibodies.slice())
    );
  }

  ngOnInit(): void {
    this._initAntibodies();
  }

  get selectedAntibodies(): Antibody[] {
    return this.recipient ? this.recipient.hla_antibodies.hla_antibodies_list : [];
  }

  get availableAntibodies(): Antibody[] {
    return this.allAntibodies.filter(a => !this.selectedAntibodies.map(i => i.code).includes(a.code));
  }

  public addAntibody(control: HTMLInputElement): void {
    if (!this.recipient || this.form.invalid) {
      return;
    }

    const { antibody, mfi } = this.form.value;
    const code = antibody instanceof Object ? antibody.code : antibody;
    const formattedCode = code.trim().toUpperCase();

    this.antibodyAdded.emit({
      code: formattedCode,
      raw_code: formattedCode,
      mfi,
      cutoff: 0
    });

    // reset form
    this.form.reset();
    this.viewForm?.resetForm('');
    this.antibodyValue = '';

    // clear and enable input
    if (control) {
      control.value = '';
      control.disabled = false;
    }
  }

  public removeAntibody(a: Antibody): void {
    if (!this.recipient) {
      return;
    }

    const index = this.recipient.hla_antibodies.hla_antibodies_list.indexOf(a);

    if (index >= 0) {
      this.recipient.hla_antibodies.hla_antibodies_list.splice(index, 1);
    }
  }

  public handleNewAntibodySelect(antibody: Antibody, control: HTMLInputElement): void {
    if (!control) {
      return;
    }
    this.antibodyValue = antibody.code ?? '';
    control.value = '';
    control.disabled = true;
  }

  public handleNewAntibodyRemove(control: HTMLInputElement): void {
    const formControl = this.form.controls.antibody;
    if (!formControl || !control) {
      return;
    }
    this.antibodyValue = '';
    formControl.setValue('');
    control.disabled = false;
  }

  public handleNewAntibodyInputEnd(value: string, control: HTMLInputElement): void {
    if (!value.length) {
      return;
    }
    this.antibodyValue = value.trim().toUpperCase();
    control.value = '';
    control.disabled = true;
  }

  public displayFn(a: Antibody): string {
    return a?.code ?? '';
  }

  private _initAntibodies(): void {
    if (!this.patients?.recipients) {
      return;
    }

    const allAntibodies = [];
    for (const r of this.patients.recipients) {
      allAntibodies.push(...r.hla_antibodies.hla_antibodies_list);
    }

    this.allAntibodies = [...new Set(allAntibodies.map(a => a.code))].map(code => {
      return { code, raw_code: code ?? '', mfi: 0, cutoff: 0 };
    }); // only unique
  }
}
