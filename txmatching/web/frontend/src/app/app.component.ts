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

  constructor(private _authService: AuthService,
              private _patientService: PatientService) {
  }

  public ngOnInit(): void {
    this._updatePatients();
  }

  /*
  *   When logged in
  *   update patients from server
  *   after every page refresh
  */
  private async _updatePatients(): Promise<void> {
    if (this._authService.isLoggedIn) {
      this.patients = await this._patientService.updatePatients();
    }
  }
}
