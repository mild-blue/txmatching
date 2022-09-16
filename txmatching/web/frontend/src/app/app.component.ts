import { Component, OnDestroy } from "@angular/core";
import { AuthService } from "@app/services/auth/auth.service";
import { Subscription } from "rxjs";
import { LoggerService } from "@app/services/logger/logger.service";
import { User } from "@app/model/User";
import { Router } from "@angular/router";
import { VersionService } from "./services/version/version.service";
import { ikem, theme } from "./model/Theme";
import { finalize, first } from "rxjs/operators";

@Component({
  selector: "app-root",
  templateUrl: "./app.component.html",
  styleUrls: ["./app.component.scss"],
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
    this._userSubscription = this._authService.currentUser.subscribe((user) => {
      this.user = user;
      if (user) {
        this._logger.log("Logged in with user", [user]);
      } else {
        this._logger.log("Logged out");
      }
    });

    this.setTheme();
  }

  setTheme() {
    let currentTheme = theme[ikem];
    this._versionService
      .initColourScheme()
      .pipe(
        first(),
        finalize(() => {
          Object.keys(currentTheme).forEach((key) => document.body.style.setProperty(`--${key}`, currentTheme[key]));

          const faviconIco = document.getElementById("favicon-ico") as HTMLLinkElement;
          if (faviconIco) {
            faviconIco.href = currentTheme["favicon-ico"];
          }
          const favicon16 = document.getElementById("favicon-16x16") as HTMLLinkElement;
          if (favicon16) {
            favicon16.href = currentTheme["favicon-16x16"];
          }
          const favicon32 = document.getElementById("favicon-32x32") as HTMLLinkElement;
          if (favicon32) {
            favicon32.href = currentTheme["favicon-32x32"];
          }
          const appleTouchIcon = document.getElementById("apple-touch-icon") as HTMLLinkElement;
          if (appleTouchIcon) {
            appleTouchIcon.href = currentTheme["apple-touch-icon"];
          }

          this.isThemeSet = true;
        })
      )
      .subscribe(
        (colour_scheme: string) => {
          currentTheme = theme[colour_scheme];
        },
        (error: string) => {
          this._logger.error("Could not set theme.", [error]);
        }
      );
  }

  ngOnDestroy() {
    this._userSubscription?.unsubscribe();
  }
}
