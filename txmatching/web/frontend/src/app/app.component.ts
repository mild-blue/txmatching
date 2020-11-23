import {Component, OnDestroy} from '@angular/core';
import {AuthService} from '@app/services/auth/auth.service';
import {Subscription} from 'rxjs';
import {LoggerService} from '@app/services/logger/logger.service';
import {User} from '@app/model/User';
import {Router} from '@angular/router';
import {VersionService} from "./services/version/version.service";
import {Version} from "./model/Version";
import {DEVELOPMENT, THEMES} from "./themes";

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
})
export class AppComponent implements OnDestroy {

  private _userSubscription?: Subscription;
  public user?: User;

  constructor(
    private _authService: AuthService,
    private _logger: LoggerService,
    private _versionService: VersionService,
    private _router: Router
  ) {
    this._userSubscription = this._authService.currentUser.subscribe(user => {
      this.user = user;
      if (user) {
        this._logger.log('Logged in with user', [user]);
      } else {
        this._logger.log('Logged out');
      }
    });

    this.setTheme()
  }

  setTheme() {
    this._versionService.getEnvironment().then((value: Version) => {
      // @ts-ignore
      let theme = THEMES[value.environment]

      if (!theme) {
        this._logger.error(`Could not find theme '${value.environment}' -> setting default '${DEVELOPMENT}'.`)
        theme = THEMES[DEVELOPMENT]
      }

      Object.keys(theme).forEach(key =>
        document.documentElement.style.setProperty(`--${key}`, theme[key])
      );

    }).catch((reason: any) => {
      this._logger.error('Could not set theme.', reason)
    })
  }

  ngOnDestroy() {
    this._userSubscription?.unsubscribe();
  }
}
