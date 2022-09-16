import { Component, OnDestroy } from "@angular/core";
import { FormControl, FormGroup, Validators } from "@angular/forms";
import { finalize, first } from "rxjs/operators";
import { Router } from "@angular/router";
import { AuthService } from "@app/services/auth/auth.service";
import { AlertService } from "@app/services/alert/alert.service";
import { LoggerService } from "@app/services/logger/logger.service";

const redirectTimeoutMs = 2000;

@Component({
  selector: "app-authentication",
  templateUrl: "./authentication.component.html",
  styleUrls: ["./authentication.component.scss"],
})
export class AuthenticationComponent implements OnDestroy {
  private _timeout?: NodeJS.Timeout;

  public form: FormGroup = new FormGroup({
    input: new FormControl([""], Validators.required),
  });

  public loading: boolean = false;
  public success: boolean = false;

  constructor(
    private _router: Router,
    private _authService: AuthService,
    private _alertService: AlertService,
    private _logger: LoggerService
  ) {}

  ngOnDestroy() {
    if (this._timeout) {
      clearTimeout(this._timeout);
    }
  }

  public onSubmit(): void {
    const input = this.form.controls.input;
    const code = input.value;

    this.loading = true;

    this._authService
      .verify(code)
      .pipe(
        first(),
        finalize(() => (this.loading = false))
      )
      .subscribe(
        () => {
          this.success = true;
          this._timeout = setTimeout(async () => this._router.navigate(["/"]), redirectTimeoutMs);
        },
        (error: Error) => {
          input.setErrors({ incorrect: true });
          this._alertService.error(`<strong>Authentication error:</strong> ${error.message}`);
          this._logger.error(error.message);
        }
      );
  }
}
