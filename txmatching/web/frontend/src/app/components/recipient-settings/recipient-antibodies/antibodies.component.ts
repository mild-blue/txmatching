import { Component, Input, ViewChild } from '@angular/core';
import { FormControl, FormGroup, NgForm, Validators } from '@angular/forms';
import { ENTER } from '@angular/cdk/keycodes';
import { ControlErrorStateMatcher } from '@app/directives/validators/form.directive';
import { Antibody } from '@app/model/Hla';
import { RecipientEditable } from '@app/model/RecipientEditable';

@Component({
  selector: 'app-recipient-antibodies',
  templateUrl: './antibodies.component.html',
  styleUrls: ['./antibodies.component.scss']
})
export class RecipientAntibodiesComponent {

  @Input() recipient?: RecipientEditable;
  @ViewChild('viewForm') viewForm?: NgForm;

  public form: FormGroup = new FormGroup({
    antibody: new FormControl('', Validators.required),
    mfi: new FormControl('', Validators.required)
  });

  public separatorKeysCodes: number[] = [ENTER];
  public errorMatcher = new ControlErrorStateMatcher();

  public antibodyValue: string = '';

  public addAntibody(control: HTMLInputElement): void {
    if (!this.recipient || this.form.invalid) {
      return;
    }

    const { antibody, mfi } = this.form.value;
    const code = antibody instanceof Object ? antibody.code : antibody;
    const formattedCode = code.trim().toUpperCase();

    this.recipient.antibodies.push({
      rawCode: formattedCode,
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
}
