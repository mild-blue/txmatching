import { Component, OnInit } from "@angular/core";
import { ActivatedRoute, Router } from "@angular/router";
import { AuthService } from "@app/services/auth/auth.service";
import { AlertService } from "@app/services/alert/alert.service";
import { VersionService } from "@app/services/version/version.service";
import { AbstractControl, FormBuilder, FormGroup, Validators } from "@angular/forms";
import { finalize } from "rxjs/operators";
import { mustMatchValidator } from "@app/directives/validators/form.directive";
import { LoggerService } from "@app/services/logger/logger.service";

@Component({
  selector: "app-reset-password",
  templateUrl: "./reset-password.component.html",
  styleUrls: ["./reset-password.component.scss"],
})
export class ResetPasswordComponent implements OnInit {
  public token?: string;

  public resetPasswordForm: FormGroup;
  public loading: boolean = false;
  public submitted: boolean = false;
  public wasReset: boolean = false;

  constructor(
    private _formBuilder: FormBuilder,
    private _router: Router,
    private _authService: AuthService,
    private _alertService: AlertService,
    private _versionService: VersionService,
    private _route: ActivatedRoute,
    private _logger: LoggerService
  ) {
    this.resetPasswordForm = this._formBuilder.group(
      {
        password: ["", [Validators.required, Validators.minLength(8)]],
        passwordRepeat: ["", [Validators.required]],
      },
      {
        validator: mustMatchValidator("password", "passwordRepeat"),
      }
    );
  }

  ngOnInit(): void {
    this.token = this._route.snapshot.paramMap.get("token") ?? undefined;
  }

  public onSubmit() {
    this.submitted = true;

    if (this.token === undefined) {
      return;
    }

    if (this.resetPasswordForm.invalid) {
      return;
    }

    const { password, passwordRepeat } = this.f;

    if (password.value != passwordRepeat.value) {
      this._alertService.error("The passwords do not match");
      return;
    }

    this.loading = true;
    this._authService
      .resetPassword(this.token, password.value)
      .pipe(finalize(() => (this.loading = false)))
      .subscribe(
        (success: boolean) => {
          if (success) {
            this._alertService.success("<strong>Success</strong> Yes.");
            this.wasReset = true;
          } else {
            this._alertService.error(
              "<strong>Password reset error:</strong> Reset token is invalid or it has expired."
            );
          }
        },
        (error: Error) => {
          this._logger.error("Password reset error", [error]);
          this._alertService.error("<strong>Password reset error:</strong> Reset token is invalid or it has expired.");
        }
      );
  }

  get f(): { [key: string]: AbstractControl } {
    return this.resetPasswordForm.controls;
  }

  public canSubmit(): boolean {
    return !!this.resetPasswordForm?.valid;
  }
}
