import { Component } from '@angular/core';
import { FormGroup } from '@angular/forms';
import { ControlErrorStateMatcher } from '@app/directives/validators/form.directive';

@Component({ template: '' })
export class AbstractFormHandlerComponent {

  public form?: FormGroup;
  public errorMatcher = new ControlErrorStateMatcher();

  constructor() {
  }

  public handleSelect(control: HTMLInputElement): void {
    if (!control) {
      return;
    }
    control.value = '';
    control.disabled = true;
  }

  public handleRemove(controlName: string, control: HTMLInputElement): void {
    const formControl = this.form?.controls[controlName];
    if (!formControl || !control) {
      return;
    }
    formControl.setValue('');
    control.disabled = false;
  }
}
