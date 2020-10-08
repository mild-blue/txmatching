import { Component, OnInit } from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { first } from 'rxjs/operators';
import { User } from '@app/model/User';
import { Router } from '@angular/router';
import { AuthService } from '@app/services/auth/auth.service';
import { AlertService } from '@app/services/alert/alert.service';
import { LoggerService } from '@app/services/logger/logger.service';

@Component({
  selector: 'app-authentication',
  templateUrl: './authentication.component.html',
  styleUrls: ['./authentication.component.scss']
})
export class AuthenticationComponent implements OnInit {

  public form: FormGroup = new FormGroup({
    input: new FormControl([''], Validators.required)
  });

  public loading: boolean = false;
  public success: boolean = false;

  constructor(private _router: Router,
              private _authService: AuthService,
              private _alertService: AlertService,
              private _logger: LoggerService) {
  }

  ngOnInit(): void {
  }

  public onSubmit(): void {
    if (this.form.invalid) {
      return;
    }

    this.loading = true;
    const code = this.form.controls.input.value;

    this._authService.verify(code).pipe(first())
    .subscribe(
      (user: User) => {
        this.success = true;
        setTimeout(() => {
          this._router.navigate(['/login']);
        }, 2000);
      },
      (error: Error) => {
        this._alertService.error(`<strong>Error while verifying:</strong> ${error.message}`);
        this._logger.error(error.message);
      },
      () => {
        this.loading = false;
      });
  }

}
