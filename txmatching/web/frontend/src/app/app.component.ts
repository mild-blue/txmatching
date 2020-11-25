import { Component, OnDestroy } from '@angular/core';
import { AuthService } from '@app/services/auth/auth.service';
import { Subscription } from 'rxjs';
import { LoggerService } from '@app/services/logger/logger.service';
import { User } from '@app/model/User';
import { Router } from '@angular/router';
import { VersionService } from './services/version/version.service';
import { development, theme } from './model/Theme';
import { finalize, first } from 'rxjs/operators';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
})
export class AppComponent implements OnDestroy {

  private _userSubscription?: Subscription;
  public user?: User;
  public isThemeSet: boolean = false;

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

    this.setTheme();
  }

  setTheme() {
    let currentTheme = theme[development];
    this._versionService.initEnvironment().pipe(
      first(),
      finalize(() => {
        Object.keys(currentTheme).forEach(key =>
          document.body.style.setProperty(`--${key}`, currentTheme[key])
        );
        this.isThemeSet = true;
      })
    ).subscribe(
      (environment: string) => {
        currentTheme = theme[environment];
      },
      (error: string) => {
        this._logger.error('Could not set theme.', [error]);
      });
  }

  ngOnDestroy() {
    this._userSubscription?.unsubscribe();
  }
}
