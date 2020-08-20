import { Component, OnInit } from '@angular/core';
import { AbstractControl, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { AuthService } from '@app/services/auth/auth.service';
import { first } from 'rxjs/operators';

@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.scss']
})
export class LoginComponent implements OnInit {
  public loginForm: FormGroup;
  public loading = false;

  submitted = false;
  error = '';
  private _returnUrl: string;

  constructor(private _formBuilder: FormBuilder,
              private _route: ActivatedRoute,
              private _router: Router,
              private _authService: AuthService) {
    if (this._authService.currentUserValue) {
      this._router.navigate(['/']);
    }
  }

  get f(): { [key: string]: AbstractControl } {
    return this.loginForm.controls;
  }

  ngOnInit(): void {
    this.loginForm = this._formBuilder.group({
      username: ['', [Validators.required, Validators.email]],
      password: ['', Validators.required]
    });

    this._returnUrl = this._route.snapshot.queryParams['returnUrl'] || '/';
  }

  onSubmit(event) {
    event.preventDefault();
    this.submitted = true;

    // stop here if form is invalid
    if (this.loginForm.invalid) {
      return;
    }

    this.loading = true;
    this._authService.login(this.f.username.value, this.f.password.value)
    .pipe(first())
    .subscribe(
      data => {
        console.log(data);
        // this._router.navigate([this._returnUrl]);
      },
      error => {
        this.error = error;
        this.loading = false;
      });
  }
}
