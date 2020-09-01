import { Component, Input } from '@angular/core';
import { User } from '@app/model/User';
import { faQuestionCircle, faUserAlt } from '@fortawesome/free-solid-svg-icons';

@Component({
  selector: 'app-header',
  templateUrl: './header.component.html',
  styleUrls: ['./header.component.scss']
})
export class HeaderComponent {

  @Input() user?: User;

  public userIcon = faUserAlt;
  public infoIcon = faQuestionCircle;

  public _openedDropdownId: string = '';

  get userDropdownId(): string {
    return 'user-dropdown';
  }

  get infoDropdownId(): string {
    return 'info-dropdown';
  }

  get openedDropdownId(): string {
    return this._openedDropdownId;
  }

  public openDropdown(id: string): void {
    this._openedDropdownId = this._openedDropdownId === id ? '' : id;
  }

  public closeDropdown(dropdownId: string): void {
    if (this._openedDropdownId === dropdownId) {
      this._openedDropdownId = '';
    }
  }
}
