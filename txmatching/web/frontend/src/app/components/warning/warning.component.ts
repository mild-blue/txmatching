import { Component, Input } from '@angular/core';

@Component({
  selector: 'app-warning',
  templateUrl: './warning.component.html',
  styleUrls: ['./warning.component.scss']
})
export class WarningComponent{
  @Input() warningType: 'warning' | 'error' | 'info' = 'info';
  @Input() data?: string[];

  constructor() { }
}
