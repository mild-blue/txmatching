import { Component, OnDestroy, OnInit } from '@angular/core';
import { Role, User } from '@app/model/User';
import { AuthService } from '@app/services/auth/auth.service';
import { faCog } from '@fortawesome/free-solid-svg-icons';
import { ConfigurationService } from '@app/services/configuration/configuration.service';
import { first } from 'rxjs/operators';
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

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.scss']
})
export class HomeComponent implements OnInit, OnDestroy {

  private _configSubscription?: Subscription;
  private _matchingSubscription?: Subscription;
  private _patientsSubscription?: Subscription;

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
              private _logger: LoggerService) {
  }

  ngOnInit(): void {
    this._initUser();
    this._initPatients();
    this._getResultsWithInitConfig();
  }

  ngOnDestroy(): void {
    this._configSubscription?.unsubscribe();
    this._matchingSubscription?.unsubscribe();
    this._patientsSubscription?.unsubscribe();
  }

  get isViewer(): boolean {
    return this.user ? this.user.decoded.role === Role.VIEWER : false;
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

  public calculate(configuration: Configuration): void {
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

    this._matchingSubscription = this._matchingService.calculate(updatedConfig)
    .pipe(first())
    .subscribe(
      (matchings: Matching[]) => {

        this.matchings = this._prepareMatchings(matchings);
        this._logger.log('Calculated matchings', [matchings]);
        this.loading = false;
      },
      error => {
        this.loading = false;
        this._alertService.error(error);
      });
  }

  private _getResultsWithInitConfig(): void {
    this.loading = true;
    this._configSubscription = this._configService.getConfiguration()
    .pipe(first())
    .subscribe(
      (config: AppConfiguration) => {
        this._logger.log('Got config from server', [config]);
        this.appConfiguration = config;
        const { scorer_constructor_name, solver_constructor_name, ...rest } = config;
        this.configuration = rest;

        this.calculate(this.configuration);
      },
      error => {
        this.loading = false;
        this._alertService.error(error);
      });
  }

  private _initUser(): void {
    this.user = this._authService.currentUserValue;
  }

  private _initPatients(): void {
    this.patients = this._patientService.getLocalPatients();
  }

  private _isDonorBloodCompatible(donor: Donor, recipient: Recipient): boolean {
    const donorBloodGroup = donor.parameters.blood_group;
    const recipientBloodGroup = recipient.parameters.blood_group;
    return compatibleBloodGroups[recipientBloodGroup].includes(donorBloodGroup);
  }

  private _prepareMatchings(m: Matching[]): Matching[] {
    return m.map((matching, key) => {
      matching.index = key + 1;
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
