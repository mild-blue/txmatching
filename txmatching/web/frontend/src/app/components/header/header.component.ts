import { Component, Input } from '@angular/core';
import { User } from '@app/model/User';
import { faQuestionCircle, faUserAlt } from '@fortawesome/free-solid-svg-icons';
import { AuthService } from '@app/services/auth/auth.service';

@Component({
  selector: 'app-header',
  templateUrl: './header.component.html',
  styleUrls: ['./header.component.scss']
})
export class HeaderComponent {

  private _openedDropdownId: string = '';

  @Input() user?: User;

  public userIcon = faUserAlt;
  public infoIcon = faQuestionCircle;

  constructor(private _authService: AuthService) {
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

  public openDropdown(id: string): void {
    this._openedDropdownId = this._openedDropdownId === id ? '' : id;
  }

  public closeDropdown(dropdownId: string): void {
    if (this._openedDropdownId === dropdownId) {
      this._openedDropdownId = '';
    }
  }

  public logOut(): void {
    this._authService.logout();
  }
}
