import { Component, OnDestroy, OnInit } from '@angular/core';
import { Role, User } from '@app/model/User';
import { AuthService } from '@app/services/auth/auth.service';
import { faCog } from '@fortawesome/free-solid-svg-icons';
import { ConfigurationService } from '@app/services/configuration/configuration.service';
import { AppConfiguration, Configuration } from '@app/model/Configuration';
import { MatchingService } from '@app/services/matching/matching.service';
import { AlertService } from '@app/services/alert/alert.service';
import { Subscription } from 'rxjs';
import { Matching, Transplant } from '@app/model/Matching';
import { compatibleBloodGroups, Donor, PatientList, Recipient } from '@app/model/Patient';
import { PatientService } from '@app/services/patient/patient.service';
import { LoggerService } from '@app/services/logger/logger.service';
import { MatchingDetailComponent } from '@app/components/matching-detail/matching-detail.component';
import { MatchingItemComponent } from '@app/components/matching-item/matching-item.component';
import { ReportService } from '@app/services/report/report.service';
import { DownloadStatus } from '@app/components/header/header.interface';

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.scss']
})
export class HomeComponent implements OnInit, OnDestroy {

  private _configSubscription?: Subscription;
  private _matchingSubscription?: Subscription;
  private _patientsSubscription?: Subscription;
  private _downloadInProgress: boolean = false;

  public loading: boolean = false;

  public matchings: Matching[] = [];
  public user?: User;
  public patients?: PatientList;
  public appConfiguration?: AppConfiguration;
  public configuration?: Configuration;

  public configIcon = faCog;
  public configOpened: boolean = false;

  public listItemComponent: typeof MatchingItemComponent = MatchingItemComponent;
  public listItemDetailComponent: typeof MatchingDetailComponent = MatchingDetailComponent;

  constructor(private _authService: AuthService,
              private _configService: ConfigurationService,
              private _alertService: AlertService,
              private _matchingService: MatchingService,
              private _patientService: PatientService,
              private _reportService: ReportService,
              private _logger: LoggerService) {
  }

  ngOnInit(): void {
    this._initUser();
    this._initMatchings();
  }

  ngOnDestroy(): void {
    this._configSubscription?.unsubscribe();
    this._matchingSubscription?.unsubscribe();
    this._patientsSubscription?.unsubscribe();
  }

  public getActiveMatching(): Matching | undefined {
    return this.matchings.find(m => m.isActive);
  }

  get isViewer(): boolean {
    return this.user ? this.user.decoded.role === Role.VIEWER : false;
  }

  get downloadStatus(): DownloadStatus {
    const activeMatchingExists = !this.loading && this.getActiveMatching() !== undefined;
    if (!activeMatchingExists) {
      return DownloadStatus.disabled;
    }
    return this._downloadInProgress ? DownloadStatus.loading : DownloadStatus.enabled;
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
    const activeMatching = this.getActiveMatching();
    if (!activeMatching) {
      return;
    }

    this._logger.log('Downloading with active matching', [activeMatching]);

    this._downloadInProgress = true;
    this._reportService.downloadReport(activeMatching.order_id).subscribe(
      (data) => {
        const blob = new Blob([data], { type: 'application/pdf' });
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        const date = new Date();
        link.href = url;
        link.download = `report-${date.getDate()}.${date.getMonth() + 1}.${date.getFullYear()}.pdf`;
        link.dispatchEvent(new MouseEvent('click'));
      },
      (error: string) => {
        this._alertService.error(`<strong>Error downloading PDF:</strong> ${error}`);
      },
      () => {
        this._downloadInProgress = false;
      });
  }

  public async calculate(configuration: Configuration): Promise<void> {
    if (!this.appConfiguration) {
      return;
    }

    if (this.configOpened) {
      this.toggleConfiguration();
    }
    this.loading = true;

    const { scorer_constructor_name, solver_constructor_name } = this.appConfiguration;
    const updatedConfig: AppConfiguration = {
      ...configuration,
      scorer_constructor_name,
      solver_constructor_name
    };
    this._logger.log('Calculating with config', [updatedConfig]);

    this.appConfiguration = updatedConfig;
    this.configuration = configuration;

    try {
      const matchings: Matching[] = await this._matchingService.calculate(updatedConfig);
      this.matchings = this._prepareMatchings(matchings);
      this._logger.log('Calculated matchings', [matchings]);
    } catch (e) {
      this._alertService.error(`Error calculating matchings: "${e}"`);
      this._logger.error(`Error calculating matchings: "${e}"`);
    } finally {
      this._logger.log('End of calculation');
      this.loading = false;
    }
  }

  private _initUser(): void {
    this.user = this._authService.currentUserValue;
  }

  private async _initMatchings(): Promise<void> {
    this.loading = true;
    try {
      // try getting patients
      try {
        this.patients = await this._patientService.getPatients();
        this._logger.log('Got patients from server', [this.patients]);
      } catch (e) {
        this._alertService.error(`Error loading patients: "${e}"`);
        this._logger.error(`Error loading patients: "${e}"`);
        return; // jump to finally block
      }

      // try getting configuration
      try {
        this.appConfiguration = await this._configService.getConfiguration();
        this._logger.log('Got config from server', [this.appConfiguration]);
      } catch (e) {
        this._alertService.error(`Error loading configuration: "${e}"`);
        this._logger.error(`Error loading configuration: "${e}"`);
        return; // jump to finally block
      }

      // when successfully got patients & configuration
      // get useful config properties
      const { scorer_constructor_name, solver_constructor_name, ...rest } = this.appConfiguration;
      this.configuration = rest;

      // calculate matchings
      await this.calculate(this.configuration);
    } catch (e) {
      // just in case
      this._alertService.error(e);
      this._logger.error(e);
    } finally {
      this._logger.log('End of matchings initialization');
      this.loading = false;
    }
  }

  private _isDonorBloodCompatible(donor: Donor, recipient: Recipient): boolean {
    const donorBloodGroup = donor.parameters.blood_group;
    const recipientBloodGroup = recipient.parameters.blood_group;
    return compatibleBloodGroups[recipientBloodGroup].includes(donorBloodGroup);
  }

  private _prepareMatchings(m: Matching[]): Matching[] {
    return m.map((matching, key) => {
      matching.index = key + 1;
      matching.isActive = key === 0;
      matching.rounds.forEach(round => round.transplants = round.transplants.map(transplant => this._prepareTransplant(transplant)));
      return matching;
    });
  }

  private _prepareTransplant(t: Transplant): Transplant {
    const transplant: Transplant = { ...t };

    // try to find Donor and Recipient instances
    if (this.patients) {
      const foundDonor = this.patients.donors.find(p => p.medical_id === t.donor);
      if (foundDonor) {
        transplant.d = foundDonor;
      }

      const foundRecipient = this.patients.recipients.find(p => p.medical_id === t.recipient);
      if (foundRecipient) {
        transplant.r = foundRecipient;
      }
    }

    if (transplant.d && transplant.r) {
      transplant.compatible_blood = this._isDonorBloodCompatible(transplant.d, transplant.r);
    }

    return transplant;
  }
}
