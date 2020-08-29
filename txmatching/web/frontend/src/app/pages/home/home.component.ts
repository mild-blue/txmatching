import { Component, OnInit } from '@angular/core';
import { User } from '@app/model/User';
import { AuthService } from '@app/services/auth/auth.service';
import { faSlidersH } from '@fortawesome/free-solid-svg-icons';
import { ConfigurationService } from '@app/services/configuration/configuration.service';
import { first } from 'rxjs/operators';
import { AppConfiguration, Configuration } from '@app/model/Configuration';

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.scss']
})
export class HomeComponent implements OnInit {

  public user?: User;
  public appConfiguration?: AppConfiguration;
  public configuration?: Configuration;
  public configIcon = faSlidersH;

  constructor(private _authService: AuthService,
              private _configService: ConfigurationService) {
  }

  ngOnInit(): void {
    this._initUser();
    this._initConfiguration();
  }

  private _initUser(): void {
    this.user = this._authService.currentUserValue;
  }

  public calculate(configuration: Configuration): void {
    const updatedConfig = {
      ...this.appConfiguration,
      ...configuration
    };
    console.log(updatedConfig);
  }

  private _initConfiguration(): void {
    this._configService.getConfiguration()
    .pipe(first())
    .subscribe((config: AppConfiguration) => {
      this.appConfiguration = config;
      const { scorer_constructor_name, solver_constructor_name, maximum_total_score, required_patient_db_ids, ...rest } = config;
      this.configuration = rest;
    });
  }

}
