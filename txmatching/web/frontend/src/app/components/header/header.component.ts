import { Component, EventEmitter, Input, Output } from '@angular/core';
import { User } from '@app/model/User';
import { faQuestionCircle, faUserAlt } from '@fortawesome/free-solid-svg-icons';
import { AuthService } from '@app/services/auth/auth.service';
import { UploadDownloadStatus } from '@app/components/header/header.interface';
import { TxmEvent, TxmEvents } from '@app/model/Event';

@Component({
  selector: 'app-header',
  templateUrl: './header.component.html',
  styleUrls: ['./header.component.scss']
})
export class HeaderComponent {

  private _openedDropdownId: string = '';

  @Input() user?: User;

  @Input() uploadStatus: UploadDownloadStatus = UploadDownloadStatus.disabled;
  @Output() uploadAction: EventEmitter<void> = new EventEmitter<void>();

  @Input() downloadStatus: UploadDownloadStatus = UploadDownloadStatus.disabled;
  @Output() downloadAction: EventEmitter<void> = new EventEmitter<void>();

  @Input() txmEvents?: TxmEvents;

  @Input() defaultTxmEvent?: TxmEvent;
  @Output() defaultTxmEventSelected: EventEmitter<number> = new EventEmitter<number>();

  public userIcon = faUserAlt;
  public infoIcon = faQuestionCircle;

  public uploadDownloadStatus: typeof UploadDownloadStatus = UploadDownloadStatus;

  constructor(private _authService: AuthService) {
  }

  get settingsDropdownId(): string {
    return 'settings-dropdown';
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

  public handleUploadClick(): void {
    this.uploadAction.emit();
  }

  public changeDefaultTxmEvent(id: number): void {
    this.defaultTxmEventSelected.emit(id);
  }
}
