import { Component, Input } from '@angular/core';
import { faSpinner } from '@fortawesome/free-solid-svg-icons';

@Component({
  selector: 'app-button',
  templateUrl: './button.component.html',
  styleUrls: ['./button.component.scss']
})
export class ButtonComponent {

  @Input() loading: boolean = false;
  @Input() disabled: boolean = false;
  @Input() success: boolean = false;
  @Input() size: 'sm' | '' = '';
  @Input() variant: 'primary' | 'success' | 'danger' | 'confirm' | 'unconfirm' = 'primary';
  @Input() type: 'submit' | 'button' | 'reset' = 'button';

  public icon = faSpinner;
}
