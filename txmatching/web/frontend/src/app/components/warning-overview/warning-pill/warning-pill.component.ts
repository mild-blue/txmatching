import { Component, Input, OnInit } from '@angular/core';

@Component({
  selector: 'app-warning-pill',
  templateUrl: './warning-pill.component.html',
  styleUrls: ['./warning-pill.component.scss']
})
export class WarningPillComponent implements OnInit{

  @Input() warningType: 'warnings' | 'errors' | 'infos' = 'infos';
  @Input() count: number = 0;
  @Input() tooltip?: string;
  @Input() generalWarning?: boolean = false;

  public matIcon: string = '';

  constructor() { }

  ngOnInit() {
    this.matIcon = this.warningType.slice(0, -1);
  }
}
