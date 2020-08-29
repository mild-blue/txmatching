import { Component, Input, OnInit } from '@angular/core';
import { User } from '@app/model/User';
import { faQuestionCircle, faUserAlt } from '@fortawesome/free-solid-svg-icons';

@Component({
  selector: 'app-header',
  templateUrl: './header.component.html',
  styleUrls: ['./header.component.scss']
})
export class HeaderComponent implements OnInit {

  @Input() user?: User;

  public userIcon = faUserAlt;
  public infoIcon = faQuestionCircle;

  public _openedDropdownId: string = '';

  constructor() {
  }

  ngOnInit(): void {
  }

  get userDropdownId(): string {
    return 'user-dropdown';
  }

  get infoDropdownId(): string {
    return 'info-dropdown';
  }

  get openedDropdownId(): string {
    return this._openedDropdownId;
  }

  closeDropdowns(): void {
    this._openedDropdownId = '';
  }

  openDropdown(id: string): void {
    this._openedDropdownId = this._openedDropdownId === id ? '' : id;
  }
}
