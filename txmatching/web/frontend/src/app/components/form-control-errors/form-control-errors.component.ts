import { Component, Input } from '@angular/core';
import { AbstractControl } from '@angular/forms';
import { errorMessages } from '@app/components/form-control-errors/form-control-errors.interface';

@Component({
  selector: 'app-form-control-errors',
  templateUrl: './form-control-errors.component.html',
  styleUrls: ['./form-control-errors.component.scss']
})
export class FormControlErrorsComponent {

  @Input() control?: AbstractControl;

  get shouldShowErrors(): boolean {
    return !!this.control && !!this.control.errors && this.control.touched;
  }

  get error(): string {
    if (!this.control?.errors) {
      return '';
    }

    const allErrors = Object.keys(this.control.errors).map(err => {
      console.log(err, errorMessages[err], this.control?.getError(err));
      if (errorMessages[err] && this.control) {
        return errorMessages[err](this.control.getError(err));
      } else {
        return 'Invalid value';
      }
    });

    // Show the most important one according to the order in errorMessages
    return allErrors[0] ?? '';
  }
}
