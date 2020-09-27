import { Injectable } from '@angular/core';
import { Donor, PatientList, patientsLSKey, Recipient } from '@app/model/Patient';
import { HttpClient } from '@angular/common/http';
import { environment } from '@environments/environment';
import { first } from 'rxjs/operators';
import { LoggerService } from '@app/services/logger/logger.service';

@Injectable({
  providedIn: 'root'
})
export class PatientService {

  constructor(private _http: HttpClient,
              private _logger: LoggerService) {
  }

  public async updatePatients(): Promise<PatientList> {
    return this._http.get<PatientList>(
      `${environment.apiUrl}/patients/`
    ).pipe(first()).toPromise();
  }

  public setLocalPatients(patients: PatientList) {
    sessionStorage.removeItem(patientsLSKey);
    sessionStorage.setItem(patientsLSKey, JSON.stringify(patients));
  }

  public getLocalPatients(): PatientList | undefined {
    const localPatients = sessionStorage.getItem(patientsLSKey);
    this._logger.log('Got patients from localhost', [localPatients]);
    return localPatients ? JSON.parse(localPatients) : undefined;
  }

  public async saveDonor(donor: Donor): Promise<Donor> {
    return this._http.put<Donor>(
      `${environment.apiUrl}/patients/donor`,
      { ...donor }
    ).pipe(first()).toPromise();
  }

  public async saveRecipient(recipient: Recipient): Promise<Recipient> {
    return this._http.put<Recipient>(
      `${environment.apiUrl}/patients/recipient`,
      { ...recipient }
    ).pipe(first()).toPromise();
  }
}
