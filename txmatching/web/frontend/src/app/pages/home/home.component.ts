import { Component, OnDestroy, OnInit } from '@angular/core';
import { AuthService } from '@app/services/auth/auth.service';
import { faCog } from '@fortawesome/free-solid-svg-icons';
import { ConfigurationService } from '@app/services/configuration/configuration.service';
import { Configuration } from '@app/model/Configuration';
import { MatchingService } from '@app/services/matching/matching.service';
import { AlertService } from '@app/services/alert/alert.service';
import { Matching } from '@app/model/Matching';
import { PatientService } from '@app/services/patient/patient.service';
import { LoggerService } from '@app/services/logger/logger.service';
import { ReportService } from '@app/services/report/report.service';
import { UploadDownloadStatus } from '@app/components/header/header.interface';
import { Report } from '@app/services/report/report.interface';
import { finalize, first } from 'rxjs/operators';
import { EventService } from '@app/services/event/event.service';
import { AbstractLoggedComponent } from '@app/pages/abstract-logged/abstract-logged.component';

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.scss']
})
export class HomeComponent extends AbstractLoggedComponent implements OnInit, OnDestroy {

  private _downloadMatchingInProgress: boolean = false;

  public matchings: Matching[] = [];

  /* All possible matchings that the solver found. This can be much higher then number of returned
   * top matchings. This is set only for AllSolution solver. */
  public foundMatchingsCount?: number;

  public configuration?: Configuration;

  public configIcon = faCog;
  public configOpened: boolean = false;

  constructor(private _matchingService: MatchingService,
              _reportService: ReportService,
              _authService: AuthService,
              _alertService: AlertService,
              _configService: ConfigurationService,
              _eventService: EventService,
              _patientService: PatientService,
              _logger: LoggerService) {
    super(_reportService, _authService, _alertService, _configService, _eventService, _patientService, _logger);
  }

  ngOnInit(): void {
    super.ngOnInit();

    this.loading = true;
    this._initAll().finally(() => this.loading = false);
  }

  ngOnDestroy(): void {
  }

  private async _initAll(): Promise<void> {
    await this._initTxmEvents();
    await this._initPatientsConfigurationMatchings();
  }

  public async setDefaultTxmEvent(eventId: number): Promise<void> {
    this.loading = true;
    this.defaultTxmEvent = await this._eventService.setDefaultEvent(eventId);
    await this._initPatientsConfigurationMatchings();
    this.loading = false;
  }

  public getActiveMatching(): Matching | undefined {
    return this.matchings.find(m => m.isActive);
  }

  get downloadMatchingStatus(): UploadDownloadStatus {
    const activeMatchingExists = !this.loading && this.getActiveMatching() !== undefined;
    if (!activeMatchingExists) {
      return UploadDownloadStatus.disabled;
    }
    return this._downloadMatchingInProgress ? UploadDownloadStatus.loading : UploadDownloadStatus.enabled;
  }

  get showConfiguration(): boolean {
    const configDefined = !!this.configuration;
    const patientsDefined = !!this.patients;
    const configIdDefined = !!this._eventService.getConfigId();
    return !this.isViewer && !this.loading && configDefined && patientsDefined && configIdDefined;
  }

  public toggleConfiguration(): void {
    this.configOpened = !this.configOpened;
  }

  get isCurrentConfigDefault(): boolean {
    return this._eventService.getConfigId() === this.defaultTxmEvent?.defaultConfigId;
  }

  get getTitleOfDefaultConfigButton(): string {
    return this.isCurrentConfigDefault
      ? `The current configuration is set as default for all users (configuration id: ${this._eventService.getConfigId()})`
      : `Set the current configuration as default for all users ` +
        `(current configuration id: ${this._eventService.getConfigId()}, ` +
        `default configuration id: ${this.defaultTxmEvent?.defaultConfigId})`;
  }

  public async setConfigAsDefault(): Promise<void> {
    if (!this.defaultTxmEvent) {
      this._logger.error('saveConfigAsDefault failed because defaultTxmEvent not set');
      return;
    }
    const configId = this._eventService.getConfigId();
    if (!configId) {
      this._logger.error('saveConfigAsDefault failed because configId not set');
      return;
    }

    try {
      const success = await this._configService.setConfigurationAsDefault(this.defaultTxmEvent.id, configId);
      await this._initTxmEvents(true);
      if (success) {
        this._alertService.success(`Default configuration for event ${this.defaultTxmEvent.name} was updated`);
      } else {
        this._alertService.error('Error occured when updating default configuration');
      }
    } catch(e) {
      this._alertService.error(`Error setting default configuration: "${e.message || e}"`);
      this._logger.error(`Error setting default configuration: "${e.message || e}"`);
    }
  }

  public async downloadMatchingPdfReport(): Promise<void> {
    if (!this.defaultTxmEvent) {
      this._logger.error('Download report failed because defaultTxmEvent not set');
      return;
    }

    const activeMatching = this.getActiveMatching();
    if (!activeMatching) {
      return;
    }

    this._logger.log('Downloading with active matching', [activeMatching]);

    this._downloadMatchingInProgress = true;
    this._reportService.downloadMatchingPdfReport(this.defaultTxmEvent.id, this._eventService.getConfigId(), activeMatching.orderId)
    .pipe(
      first(),
      finalize(() => this._downloadMatchingInProgress = false)
    )
    .subscribe(
      (report: Report) => {
        const blob = new Blob([report.data], { type: 'application/pdf' });
        const link = document.createElement('a');
        link.href = window.URL.createObjectURL(blob);
        link.download = report.filename;
        link.dispatchEvent(new MouseEvent('click'));
      },
      (error: Error) => {
        this._alertService.error(`<strong>Error downloading PDF:</strong> ${error.message}`);
      });
  }

  public async calculate(configuration: Configuration): Promise<void> {
    if (!this.patients) {
      this._logger.error('Calculate failed because patients not set');
      return;
    }
    if (!this.defaultTxmEvent) {
      this._logger.error('Calculate failed because defaultTxmEvent not set');
      return;
    }

    if (this.configOpened) {
      this.toggleConfiguration();
    }
    this.loading = true;
    this.matchings = [];
    this.foundMatchingsCount = 0;

    this._logger.log('Calculating with config', [configuration]);

    this.configuration = configuration;

    try {
      const calculatedMatchings = await this._matchingService.calculate(
        this.defaultTxmEvent.id, configuration, this.patients
      );
      this.matchings = calculatedMatchings.calculatedMatchings;
      this._eventService.setConfigId(calculatedMatchings.configId);
      this.foundMatchingsCount = calculatedMatchings.foundMatchingsCount;
      this._logger.log('Calculated matchings', [calculatedMatchings]);
      if (calculatedMatchings.showNotAllMatchingsFound) {
        this._alertService.info(`
        There exist more than ${this.foundMatchingsCount} matchings. Shown matchings present the top matchings found so
         far, most probably including the top matching over all. Try using the ILPSolver to find possible better
         matching or contact the developers for more details using info@mild.blue or call +420 723 927 536.`);
      }
    } catch (e) {
      this._alertService.error(`Error calculating matchings: "${e.message || e}"`);
      this._logger.error(`Error calculating matchings: "${e.message || e}"`);
    } finally {
      this._logger.log('End of calculation');
      this.loading = false;
    }
  }

  private async _initPatientsConfigurationMatchings(): Promise<void> {
    if(!this.defaultTxmEvent) {
      this._logger.error('Init matchings failed because defaultTxmEvent not set');
      return;
    }

    // We could possibly run _initPatients and _initConfiguration in parallel (using Promise.all), but we don't
    // because due to the current BE limitations, it would not improve the performance significantly,
    // and could introduce some risks
    await this._initPatients(false);
    await this._initConfiguration();
    await this._initMatchings();

    this._logger.log('End of matchings initialization');
  }

  private async _initMatchings(): Promise<void> {
    if(!this.configuration) {
      this._logger.error('Init matchings failed because configuration not set');
      return;
    }

    await this.calculate(this.configuration);
  }
}
