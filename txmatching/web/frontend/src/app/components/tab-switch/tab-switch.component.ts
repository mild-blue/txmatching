import { Component, EventEmitter, Input, OnInit, Output } from '@angular/core';

@Component({
  selector: 'app-tab-switch',
  templateUrl: './tab-switch.component.html',
  styleUrls: ['./tab-switch.component.scss']
})
export class TabSwitchComponent implements OnInit {

  @Input() tabs: string[] = [];
  @Input() activeTab?: string;
  @Output() tabClicked: EventEmitter<string> = new EventEmitter<string>();

  constructor() {
  }

  ngOnInit(): void {
  }

  public handleClick(tab: string): void {
    this.tabClicked.emit(tab);
  }

}
