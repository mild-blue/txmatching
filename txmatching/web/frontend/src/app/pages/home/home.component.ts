import { Component, OnInit } from '@angular/core';
import { User } from '@app/model/User';
import { AuthService } from '@app/services/auth/auth.service';
import { faSlidersH } from '@fortawesome/free-solid-svg-icons';
import { ConfigurationService } from '@app/services/configuration/configuration.service';

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.scss']
})
export class HomeComponent implements OnInit {

  public user?: User;
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

  private _initConfiguration(): void {
    this._configService.getConfiguration();
  }

}
