import { Component, Input, OnInit } from '@angular/core';

@Component({
  selector: 'app-warning',
  templateUrl: './warning.component.html',
  styleUrls: ['./warning.component.scss']
})
export class WarningComponent implements OnInit{
  @Input() warningType: 'warnings' | 'errors' | 'infos' = 'infos';
  @Input() data?: string[];

  public matIcon: string = '';

  constructor() { }

  ngOnInit() {
    this.matIcon = this.warningType.slice(0, -1);
  }
}
