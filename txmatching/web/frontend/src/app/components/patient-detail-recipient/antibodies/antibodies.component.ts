import { Component, Input, OnInit, ViewChild } from '@angular/core';
import { FormControl, FormGroup, NgForm, Validators } from '@angular/forms';
import { Antibody, PatientList, Recipient } from '@app/model/Patient';
import { Observable } from 'rxjs';
import { ENTER } from '@angular/cdk/keycodes';
import { antibodiesFullTextSearch, ConfigErrorStateMatcher } from '@app/directives/validators/configForm.directive';
import { map, startWith } from 'rxjs/operators';

@Component({
  selector: 'app-antibodies',
  templateUrl: './antibodies.component.html',
  styleUrls: ['./antibodies.component.scss']
})
export class AntibodiesComponent implements OnInit {

  @Input() patients?: PatientList;
  @Input() recipient?: Recipient;

  @ViewChild('viewForm') viewForm?: NgForm;

  public form: FormGroup = new FormGroup({
    antibody: new FormControl('', Validators.required),
    mfi: new FormControl('', Validators.required)
  });

  public allAntibodies: Antibody[] = [];
  public filteredAntibodies: Observable<Antibody[]>;

  public separatorKeysCodes: number[] = [ENTER];
  public errorMatcher = new ConfigErrorStateMatcher();

  public antibodyValue: string = '';

  constructor() {
    this.filteredAntibodies = this.form.controls.antibody.valueChanges.pipe(
      startWith(''),
      map((value: string | Antibody) => {
        return !value || typeof value === 'string' ? value : value.code;
      }),
      map(code => code ? antibodiesFullTextSearch(this.availableAntibodies, code) : this.availableAntibodies.slice())
    );
  }

  ngOnInit(): void {
    this._initAntibodies();
  }

  get selectedAntibodies(): Antibody[] {
    return this.recipient ? this.recipient.hla_antibodies.antibodies_list : [];
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

    this.recipient.hla_antibodies.antibodies_list.push({
      code,
      mfi
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

    const index = this.recipient.hla_antibodies.antibodies_list.indexOf(a);

    if (index >= 0) {
      this.recipient.hla_antibodies.antibodies_list.splice(index, 1);
    }
  }

  public handleNewAntibodySelect(antibody: Antibody, control: HTMLInputElement): void {
    if (!control) {
      return;
    }
    this.antibodyValue = antibody.code;
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
    this.antibodyValue = value;
    control.value = '';
    control.disabled = true;
  }

  public displayFn(a: Antibody): string {
    return a && a.code ? a.code : '';
  }

  private _initAntibodies(): void {
    if (!this.patients || !this.patients.recipients) {
      return;
    }

    const allAntibodies = [];
    for (const r of this.patients.recipients) {
      allAntibodies.push(...r.hla_antibodies.antibodies_list);
    }

    this.allAntibodies = [...new Set(allAntibodies)]; // only unique
  }
}
