import { Component, OnInit } from '@angular/core';
import { AbstractControl, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { AuthService } from '@app/services/auth/auth.service';
import { first } from 'rxjs/operators';
import { AlertService } from '@app/services/alert/alert.service';

@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.scss']
})
export class LoginComponent implements OnInit {

  public loginForm: FormGroup;
  public loading: boolean = false;
  public submitted: boolean = false;

  constructor(private _formBuilder: FormBuilder,
              private _route: ActivatedRoute,
              private _router: Router,
              private _authService: AuthService,
              private _alertService: AlertService) {
    this.loginForm = this._formBuilder.group({
      email: ['', [Validators.required, Validators.email]],
      password: ['', Validators.required]
    });
  }

  ngOnInit(): void {
    if (this._authService.currentUserValue) {
      this._navigateToHomepage();
    }
  }

  private _navigateToHomepage(): void {
    this._router.navigate(['/']);
  }

  public onSubmit() {

    this.submitted = true;

    if (this.loginForm.invalid) {
      return;
    }

    this.loading = true;
    const { email, password } = this.f;

    this._authService.login(email.value, password.value)
    .pipe(first())
    .subscribe(
      () => this._navigateToHomepage(),
      error => {
        this.loading = false;
        this._alertService.error(error);
      });
  }

  get f(): { [key: string]: AbstractControl } {
    return this.loginForm.controls;
  }
}
