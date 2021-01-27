import { Component, OnInit } from '@angular/core';
import { TxmEvent, TxmEvents } from '@app/model/Event';
import { EventService } from '@app/services/event/event.service';
import { LoggerService } from '@app/services/logger/logger.service';
import { AlertService } from '@app/services/alert/alert.service';
import { Role, User } from '@app/model';
import { AuthService } from '@app/services/auth/auth.service';

@Component({ template: '' })
export class AbstractLoggedComponent implements OnInit {

  public txmEvents?: TxmEvents;
  public defaultTxmEvent?: TxmEvent;
  public user?: User;

  constructor(protected _authService: AuthService,
              protected _alertService: AlertService,
              protected _eventService: EventService,
              protected _logger: LoggerService) { }

  ngOnInit(): void {
    this.user = this._authService.currentUserValue;
  }

  get isViewer(): boolean {
    return this.user ? this.user.decoded.role === Role.VIEWER : false;
  }

  protected async _initTxmEvents(): Promise<void> {
    try {
      this.txmEvents = await this._eventService.getEvents();
      this._logger.log('Got txm events from server', [this.txmEvents]);
      this.defaultTxmEvent = await this._eventService.getDefaultEvent();
      this._logger.log('Got default txm event from server', [this.defaultTxmEvent]);
    } catch (e) {
      this._alertService.error(`Error loading txm events: "${e.message || e}"`);
      this._logger.error(`Error loading txm events: "${e.message || e}"`);
    }
  }

}
