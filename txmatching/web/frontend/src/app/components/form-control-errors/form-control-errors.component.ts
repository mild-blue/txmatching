import { Component, Input } from '@angular/core';
import { AbstractControl } from '@angular/forms';
import { errorMessages } from '@app/components/form-control-errors/form-control-errors.interface';

@Component({
  selector: 'app-form-control-errors',
  templateUrl: './form-control-errors.component.html',
  styleUrls: ['./form-control-errors.component.scss']
})
export class FormControlErrorsComponent {

  @Input() control?: AbstractControl | null;

  get errors(): string[] {
    if (!this.control?.errors || !this.control.touched) {
      return [];
    }

    return Object.keys(this.control.errors).map(err => {
      if (errorMessages[err] && this.control) {
        return errorMessages[err](this.control.getError(err));
      } else {
        return 'Invalid value';
      }
    });
  }
}
