import { Component, OnDestroy, OnInit } from '@angular/core';
import { User } from '@app/model/User';
import { AuthService } from '@app/services/auth/auth.service';
import { faCog, faTimes } from '@fortawesome/free-solid-svg-icons';
import { ConfigurationService } from '@app/services/configuration/configuration.service';
import { first } from 'rxjs/operators';
import { AppConfiguration, Configuration } from '@app/model/Configuration';
import { MatchingService } from '@app/services/matching/matching.service';
import { AlertService } from '@app/services/alert/alert.service';
import { Subscription } from 'rxjs';
import { Matching, MatchingView } from '@app/model/Matching';
import { PatientList } from '@app/model/Patient';
import { PatientService } from '@app/services/patient/patient.service';
import { LoggerService } from '@app/services/logger/logger.service';

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

  public matchings: MatchingView[] = [];
  public user?: User;
  public appConfiguration?: AppConfiguration;
  public configuration?: Configuration;
  public patients: PatientList;

  public configIcon = faCog;
  public closeIcon = faTimes;
  public configOpened: boolean = false;

  constructor(private _authService: AuthService,
              private _configService: ConfigurationService,
              private _alertService: AlertService,
              private _matchingService: MatchingService,
              private _patientService: PatientService,
              private _logger: LoggerService) {
    this.patients = this._patientService.getPatients();
  }

  ngOnInit(): void {
    this._initUser();
    this._getResultsWithInitConfig();
  }

  ngOnDestroy(): void {
    this._configSubscription?.unsubscribe();
    this._matchingSubscription?.unsubscribe();
    this._patientsSubscription?.unsubscribe();
  }

  public toggleConfiguration(): void {
    this.configOpened = !this.configOpened;
  }

  public calculate(configuration: Configuration): void {
    if (!this.appConfiguration) {
      return;
    }

    this.configOpened = false;
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
        this.matchings = matchings.map((m, key) => {
          return { index: key + 1, ...m };
        });
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

}
