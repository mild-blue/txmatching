import { Component, OnInit } from '@angular/core';
import { PatientService } from '@app/services/patient/patient.service';
import { AuthService } from '@app/services/auth/auth.service';
import { PatientList } from '@app/model/Patient';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
})
export class AppComponent implements OnInit {

  public patients?: PatientList;
  public loggedIn: boolean = false;

  constructor(private _authService: AuthService,
              private _patientService: PatientService) {
  }

  public ngOnInit(): void {
    this.loggedIn = this._authService.isLoggedIn;
    this._updatePatients();
  }

  /*
  *   When logged in
  *   update patients from server
  *   after every page refresh
  */
  private async _updatePatients(): Promise<void> {
    if (this.loggedIn) {
      this.patients = await this._patientService.updatePatients();
    }
  }
}
