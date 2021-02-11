import { Component, OnDestroy, OnInit } from '@angular/core';
import { Role, User } from '@app/model/User';
import { AuthService } from '@app/services/auth/auth.service';
import { faCog } from '@fortawesome/free-solid-svg-icons';
import { ConfigurationService } from '@app/services/configuration/configuration.service';
import { AppConfiguration, Configuration } from '@app/model/Configuration';
import { MatchingService } from '@app/services/matching/matching.service';
import { AlertService } from '@app/services/alert/alert.service';
import { Matching } from '@app/model/Matching';
import { PatientService } from '@app/services/patient/patient.service';
import { LoggerService } from '@app/services/logger/logger.service';
import { ReportService } from '@app/services/report/report.service';
import { UploadDownloadStatus } from '@app/components/header/header.interface';
import { Report } from '@app/services/report/report.interface';
import { finalize, first } from 'rxjs/operators';
import { PatientList } from '@app/model/PatientList';
import { UploadService } from '@app/services/upload/upload.service';
import { EventService } from '@app/services/event/event.service';
import { AbstractLoggedComponent } from '@app/pages/abstract-logged/abstract-logged.component';

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.scss']
})
export class HomeComponent extends AbstractLoggedComponent implements OnInit, OnDestroy {

  private _downloadInProgress: boolean = false;
  private _uploadInProgress: boolean = false;

  public loading: boolean = false;

  public matchings: Matching[] = [];
  public foundMatchingsCount: number = 0;

  public patients?: PatientList;
  public appConfiguration?: AppConfiguration;
  public configuration?: Configuration;

  public configIcon = faCog;
  public configOpened: boolean = false;

  constructor(private _configService: ConfigurationService,
              private _matchingService: MatchingService,
              private _patientService: PatientService,
              private _reportService: ReportService,
              private _uploadService: UploadService,
              _authService: AuthService,
              _alertService: AlertService,
              _eventService: EventService,
              _logger: LoggerService) {
    super(_authService, _alertService, _eventService, _logger);
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
    await this._initMatchings();
  }

  public async setDefaultTxmEvent(event_id: number): Promise<void> {
    this.loading = true;
    this.defaultTxmEvent = await this._eventService.setDefaultEvent(event_id);
    await this._initMatchings();
    this.loading = false;
  }

  public getActiveMatching(): Matching | undefined {
    return this.matchings.find(m => m.isActive);
  }

  get downloadStatus(): UploadDownloadStatus {
    const activeMatchingExists = !this.loading && this.getActiveMatching() !== undefined;
    if (!activeMatchingExists) {
      return UploadDownloadStatus.disabled;
    }
    return this._downloadInProgress ? UploadDownloadStatus.loading : UploadDownloadStatus.enabled;
  }

  get uploadStatus(): UploadDownloadStatus {
    if (this.loading) {
      return UploadDownloadStatus.disabled;
    }
    return this._uploadInProgress ? UploadDownloadStatus.loading : UploadDownloadStatus.enabled;
  }

  get showConfiguration(): boolean {
    const configDefined = !!this.configuration;
    const patientsDefined = !!this.patients;
    return !this.isViewer && !this.loading && configDefined && patientsDefined;
  }

  public toggleConfiguration(): void {
    this.configOpened = !this.configOpened;
    document.querySelector('body')?.classList.toggle('config-opened');
  }

  public async downloadReport(): Promise<void> {
    if(!this.defaultTxmEvent) {
      this._logger.error(`Download report failed because defaultTxmEvent not set`);
      return;
    }

    const activeMatching = this.getActiveMatching();
    if (!activeMatching) {
      return;
    }

    this._logger.log('Downloading with active matching', [activeMatching]);

    this._downloadInProgress = true;
    this._reportService.downloadReport(this.defaultTxmEvent.id, activeMatching.order_id)
    .pipe(
      first(),
      finalize(() => this._downloadInProgress = false)
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

  public uploadPatients(): void {
    if(!this.defaultTxmEvent) {
      this._logger.error(`uploadPatients failed because defaultTxmEvent not set`);
      return;
    }
    this._uploadService.uploadFile(
      this.defaultTxmEvent.id, 'Recalculate matchings', this._initMatchings.bind(this)
    );
  }

  public async calculate(configuration: Configuration): Promise<void> {
    if(!this.appConfiguration) {
      this._logger.error(`Calculate failed because appConfiguration not set`);
      return;
    }
    if(!this.patients) {
      this._logger.error(`Calculate failed because patients not set`);
      return;
    }
    if(!this.defaultTxmEvent) {
      this._logger.error(`Calculate failed because defaultTxmEvent not set`);
      return;
    }

    if (this.configOpened) {
      this.toggleConfiguration();
    }
    this.loading = true;
    this.matchings = [];
    this.foundMatchingsCount = 0;

    const { scorer_constructor_name } = this.appConfiguration;
    const updatedConfig: AppConfiguration = {
      ...configuration,
      scorer_constructor_name
    };
    this._logger.log('Calculating with config', [updatedConfig]);

    this.appConfiguration = updatedConfig;
    this.configuration = configuration;

    try {
      const calculatedMatchings = await this._matchingService.calculate(
        this.defaultTxmEvent.id, updatedConfig, this.patients
      );
      this.matchings = calculatedMatchings.calculated_matchings;
      this.foundMatchingsCount = calculatedMatchings.found_matchings_count;
      this._logger.log('Calculated matchings', [calculatedMatchings]);
      if (calculatedMatchings.show_not_all_matchings_found) {
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

  private async _initMatchings(): Promise<void> {
    if(!this.defaultTxmEvent) {
      this._logger.error(`Init matchings failed because defaultTxmEvent not set`);
      return;
    }

    try {
      // try getting patients
      try {
        this.patients = await this._patientService.getPatients(this.defaultTxmEvent.id);
        this._logger.log('Got patients from server', [this.patients]);
      } catch (e) {
        this._alertService.error(`Error loading patients: "${e.message || e}"`);
        this._logger.error(`Error loading patients: "${e.message || e}"`);
        return; // jump to finally block
      }

      // try getting configuration
      try {
        this.appConfiguration = await this._configService.getConfiguration(this.defaultTxmEvent.id);
        this._logger.log('Got config from server', [this.appConfiguration]);
      } catch (e) {
        this._alertService.error(`Error loading configuration: "${e.message || e}"`);
        this._logger.error(`Error loading configuration: "${e.message || e}"`);
        return; // jump to finally block
      }

      // when successfully got patients & configuration
      // get useful config properties
      const {scorer_constructor_name, ...rest} = this.appConfiguration;
      this.configuration = rest;

      // calculate matchings
      await this.calculate(this.configuration);
    } catch (e) {
      // just in case
      this._alertService.error(e);
      this._logger.error(e);
    } finally {
      this._logger.log('End of matchings initialization');
    }
  }
}
