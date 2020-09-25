import { Component, OnDestroy } from '@angular/core';
import { PatientService } from '@app/services/patient/patient.service';
import { AuthService } from '@app/services/auth/auth.service';
import { PatientList } from '@app/model/Patient';
import { Subscription } from 'rxjs';
import { LoggerService } from '@app/services/logger/logger.service';
import { User } from '@app/model/User';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
})
export class AppComponent implements OnDestroy {

  public patients?: PatientList;
  public user?: User;
  private _userSubscription?: Subscription;

  constructor(private _authService: AuthService,
              private _logger: LoggerService,
              private _patientService: PatientService) {
    this._userSubscription = this._authService.currentUser.subscribe(user => {
      this.user = user;
      if (user) {
        this._logger.log('Logged in with user', [user]);
        this._updatePatients();
      }
    });
  }

  ngOnDestroy() {
    this._userSubscription?.unsubscribe();
  }

  get isLoggedIn(): boolean {
    return this._authService.isLoggedIn;
  }

  get shouldLoadContent(): boolean {
    return !this.isLoggedIn || this.patients !== undefined;
  }

  private async _updatePatients(): Promise<void> {
    this._patientService.updatePatients().then(patients => {
      this._logger.log('Got patients from server', [patients]);
      this.patients = patients;
      this._patientService.setLocalPatients(patients);
    });
  }
}
