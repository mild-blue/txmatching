import { Component, Input } from '@angular/core';
import { WarningType } from '@app/helpers/messages';

@Component({
  selector: 'app-warning-pill',
  templateUrl: './warning-pill.component.html',
  styleUrls: ['./warning-pill.component.scss']
})
export class WarningPillComponent{

  @Input() warningType: WarningType = 'info';
  @Input() count: number = 0;
  @Input() tooltip?: string;
  @Input() generalWarning?: boolean = false;

  constructor() { }
}
