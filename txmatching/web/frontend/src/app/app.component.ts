import { Component, OnInit } from '@angular/core';
import { PatientService } from '@app/services/patient/patient.service';
import { AuthService } from '@app/services/auth/auth.service';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
})
export class AppComponent implements OnInit {

  constructor(private _authService: AuthService,
              private _patientService: PatientService) {
  }

  public ngOnInit(): void {
    if (this._authService.isLoggedIn) {
      this._patientService.updatePatients();
    }
  }
}
