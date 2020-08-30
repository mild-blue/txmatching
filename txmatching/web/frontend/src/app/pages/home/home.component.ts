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
import { Patient } from '@app/model/Patient';
import { PatientService } from '@app/services/patient/patient.service';

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.scss']
})
export class HomeComponent implements OnInit, OnDestroy {

  public loading: boolean = false;
  private _configSubscription?: Subscription;
  public matchings: MatchingView[] = [];
  public patients: Patient[] = [];

  public user?: User;
  public appConfiguration?: AppConfiguration;
  public configuration?: Configuration;
  private _matchingSubscription?: Subscription;
  private _patientsSubscription?: Subscription;

  public configIcon = faCog;
  public closeIcon = faTimes;
  public configOpened: boolean = false;

  constructor(private _authService: AuthService,
              private _configService: ConfigurationService,
              private _alertService: AlertService,
              private _matchingService: MatchingService,
              private _patientService: PatientService) {
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

  public calculate(configuration: Configuration): void {
    if (!this.appConfiguration) {
      return;
    }

    this.configOpened = false;
    this.loading = true;

    const { scorer_constructor_name, solver_constructor_name, maximum_total_score, required_patient_db_ids } = this.appConfiguration;
    const updatedConfig: AppConfiguration = {
      ...configuration,
      scorer_constructor_name,
      solver_constructor_name,
      maximum_total_score,
      required_patient_db_ids
    };
    console.log('Calculating with config', updatedConfig);

    this.appConfiguration = updatedConfig;
    this.configuration = configuration;

    this._matchingSubscription = this._matchingService.calculate(updatedConfig)
    .pipe(first())
    .subscribe(
      (matchings: Matching[]) => {
        // todo: show only X at a time
        this.matchings = matchings.slice(0, 10).map((m, key) => {
          return { index: key + 1, ...m };
        });
        console.log('Calculated matchings', matchings);
        this.loading = false;
        console.log('Loading?', this.loading);
      },
      error => {
        this.loading = false;
        this._alertService.error(error);
      });
  }

  private _initPatients(): void {
    this._patientsSubscription = this._patientService.getPatients()
    .pipe(first())
    .subscribe((patients: Patient[]) => {
      console.log('Loaded patients', patients);
      this.patients = patients;
    });
  }

  private _getResultsWithInitConfig(): void {
    this.loading = true;
    this._configSubscription = this._configService.getConfiguration()
    .pipe(first())
    .subscribe(
      (config: AppConfiguration) => {
        console.log('Got config from server', config);
        this.appConfiguration = config;
        const { scorer_constructor_name, solver_constructor_name, maximum_total_score, required_patient_db_ids, ...rest } = config;
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

  public toggleConfiguration(): void {
    this.configOpened = !this.configOpened;
  }

}
