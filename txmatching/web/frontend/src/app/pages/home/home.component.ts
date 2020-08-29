import { Component, OnDestroy, OnInit } from '@angular/core';
import { User } from '@app/model/User';
import { AuthService } from '@app/services/auth/auth.service';
import { faSlidersH, faTimes } from '@fortawesome/free-solid-svg-icons';
import { ConfigurationService } from '@app/services/configuration/configuration.service';
import { first } from 'rxjs/operators';
import { AppConfiguration, Configuration } from '@app/model/Configuration';
import { MatchingService } from '@app/services/matching/matching.service';
import { AlertService } from '@app/services/alert/alert.service';
import { Subscription } from 'rxjs';

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.scss']
})
export class HomeComponent implements OnInit, OnDestroy {

  public loading: boolean = false;
  private _configSubscription?: Subscription;

  public user?: User;
  public appConfiguration?: AppConfiguration;
  public configuration?: Configuration;
  public configIcon = faSlidersH;
  public closeIcon = faTimes;
  public configOpened: boolean = false;
  private _matchingSubscription?: Subscription;

  constructor(private _authService: AuthService,
              private _configService: ConfigurationService,
              private _alertService: AlertService,
              private _matchingService: MatchingService) {
  }

  ngOnInit(): void {
    this._initUser();
    this._getResultsWithInitConfig();
  }

  ngOnDestroy(): void {
    this._configSubscription?.unsubscribe();
    this._matchingSubscription?.unsubscribe();
  }

  public calculate(configuration: Configuration): void {
    if (!this.appConfiguration) {
      return;
    }

    const { scorer_constructor_name, solver_constructor_name, maximum_total_score, required_patient_db_ids } = this.appConfiguration;
    const updatedConfig: AppConfiguration = {
      ...configuration,
      scorer_constructor_name,
      solver_constructor_name,
      maximum_total_score,
      required_patient_db_ids
    };
    console.log(updatedConfig);

    this._matchingSubscription = this._matchingService.calculate(updatedConfig)
    .pipe(first())
    .subscribe(
      (r: any) => {
        this.loading = false;
        console.log(r);
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
