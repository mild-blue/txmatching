import { Component, OnInit } from '@angular/core';
import { TxmEvent, TxmEvents } from '@app/model/Event';
import { EventService } from '@app/services/event/event.service';
import { LoggerService } from '@app/services/logger/logger.service';
import { AlertService } from '@app/services/alert/alert.service';
import { AppConfiguration, PatientList, Role, User } from '@app/model';
import { AuthService } from '@app/services/auth/auth.service';
import { ConfigurationService } from '@app/services/configuration/configuration.service';
import { PatientService } from '@app/services/patient/patient.service';

@Component({ template: '' })
export class AbstractLoggedComponent implements OnInit {

  public txmEvents?: TxmEvents;
  public defaultTxmEvent?: TxmEvent;
  public user?: User;
  public appConfiguration?: AppConfiguration;
  public patients?: PatientList;

  constructor(protected _authService: AuthService,
              protected _alertService: AlertService,
              protected _configService: ConfigurationService,
              protected _eventService: EventService,
              protected _patientService: PatientService,
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
      this.defaultTxmEvent = await this._eventService.getDefaultEvent();
    } catch (e) {
      this._alertService.error(`Error loading txm events: "${e.message || e}"`);
      this._logger.error(`Error loading txm events: "${e.message || e}"`);
    }
  }

  protected async _initAppConfiguration(): Promise<void> {
    if(!this.defaultTxmEvent) {
      this._logger.error(`Configuration init failed because defaultTxmEvent not set`);
      return;
    }

    try {
      this.appConfiguration = await this._configService.getAppConfiguration(this.defaultTxmEvent.id);
      this._logger.log('Got config from server', [this.appConfiguration]);
    } catch (e) {
      this._alertService.error(`Error loading configuration: "${e.message || e}"`);
      this._logger.error(`Error loading configuration: "${e.message || e}"`);
    }
  }

  protected async _initPatients(): Promise<void> {
    if(!this.defaultTxmEvent) {
      this._logger.error(`Init patients failed because defaultTxmEvent not set`);
      return;
    }

    try {
      this.patients = await this._patientService.getPatients(this.defaultTxmEvent.id);
      this._logger.log('Got patients from server', [this.patients]);
    } catch (e) {
      this._alertService.error(`Error loading patients: "${e.message || e}"`);
      this._logger.error(`Error loading patients: "${e.message || e}"`);
      throw e;
    }
  }
}
