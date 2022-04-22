import { Component } from '@angular/core';
import { AbstractControl, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { AuthService } from '@app/services/auth/auth.service';
import { finalize, first } from 'rxjs/operators';
import { AlertService } from '@app/services/alert/alert.service';
import { User } from '@app/model/User';
import { VersionService } from '@app/services/version/version.service';
import { staging } from '@app/model/Theme';
import { UserTokenType } from '@app/model/enums/UserTokenType';

@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.scss']
})
export class LoginComponent {

  public loginForm: FormGroup;
  public loading: boolean = false;
  public submitted: boolean = false;
  public showInfoText: boolean = false;

  constructor(private _formBuilder: FormBuilder,
              private _router: Router,
              private _authService: AuthService,
              private _alertService: AlertService,
              private _versionService: VersionService) {
    this._initInfoText();
    this.loginForm = this._formBuilder.group({
      email: ['', [Validators.required]], // TODO: add Validators.email when relevant
      password: ['', Validators.required]
    });
  }

  private _initInfoText(): void {
    const environment = this._versionService.getEnvironment();
    if (environment === staging) {
      this.showInfoText = true;
    }
  }

  public onSubmit() {

    this.submitted = true;

    if (this.loginForm.invalid) {
      return;
    }

    this.loading = true;
    const { email, password } = this.f;

    this._authService.login(email.value, password.value)
    .pipe(
      first(),
      finalize(() => this.loading = false)
    )
    .subscribe(
      (user: User) => {
        if (user.decoded.type === UserTokenType.OTP) {
          this._router.navigate(['authentication']);
        } else if (user.decoded.type === UserTokenType.ACCESS) {
          this._router.navigate(['/']);
        } else {
          this._alertService.error('<strong>Authentication error:</strong> Unexpected token received, contact administrator.');
        }
      },
      (error: Error) => {
        this._alertService.error(`<strong>Authentication error:</strong> ${error.message}`);
      });
  }

  get f(): { [key: string]: AbstractControl; } {
    return this.loginForm.controls;
  }
}
