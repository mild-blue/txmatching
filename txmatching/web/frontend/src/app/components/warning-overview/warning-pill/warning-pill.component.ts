import { Component, Input } from '@angular/core';

@Component({
  selector: 'app-warning-pill',
  templateUrl: './warning-pill.component.html',
  styleUrls: ['./warning-pill.component.scss']
})
export class WarningPillComponent{

  @Input() warningType: 'warning' | 'error' | 'info' = 'info';
  @Input() count: number = 0;
  @Input() tooltip?: string;
  @Input() generalWarning?: boolean = false;

  constructor() { }
}
