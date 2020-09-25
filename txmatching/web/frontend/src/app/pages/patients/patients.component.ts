import { Component, OnInit } from '@angular/core';
import { PatientList } from '@app/model/Patient';
import { PatientService } from '@app/services/patient/patient.service';

@Component({
  selector: 'app-patients',
  templateUrl: './patients.component.html',
  styleUrls: ['./patients.component.scss']
})
export class PatientsComponent implements OnInit {

  public patients?: PatientList;

  constructor(private _patientService: PatientService) {
  }

  ngOnInit(): void {
    this._initPatients();
  }

  get patientsCount(): number {
    return this.patients ? this.patients.donors.length + this.patients.recipients.length : 0;
  }

  private _initPatients(): void {
    this.patients = this._patientService.getLocalPatients();
  }
}
