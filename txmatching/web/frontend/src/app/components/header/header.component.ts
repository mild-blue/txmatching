import { Component, EventEmitter, Input, Output } from '@angular/core';
import { User } from '@app/model/User';
import { faQuestionCircle, faUserAlt } from '@fortawesome/free-solid-svg-icons';
import { AuthService } from '@app/services/auth/auth.service';
import { DownloadStatus } from '@app/components/header/header.interface';

@Component({
  selector: 'app-header',
  templateUrl: './header.component.html',
  styleUrls: ['./header.component.scss']
})
export class HeaderComponent {

  private _openedDropdownId: string = '';

  @Input() user?: User;
  @Input() downloadStatus: DownloadStatus = DownloadStatus.disabled;
  @Output() downloadAction: EventEmitter<void> = new EventEmitter<void>();

  public userIcon = faUserAlt;
  public infoIcon = faQuestionCircle;

  public downloadStatusOptions: typeof DownloadStatus = DownloadStatus;

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

  public handleDownloadClick(): void {
    this.downloadAction.emit();
  }
}
