import { Injectable } from '@angular/core';
import { Observable, of } from 'rxjs';
import { Patient, patientsLSKey } from '@app/model/Patient';
import { HttpClient } from '@angular/common/http';
import { environment } from '@environments/environment';
import { map } from 'rxjs/operators';
import { LoggerService } from '@app/services/logger/logger.service';

@Injectable({
  providedIn: 'root'
})
export class PatientService {

  private static _updateLocalStorage(patients: Patient[]) {
    sessionStorage.removeItem(patientsLSKey);
    sessionStorage.setItem(patientsLSKey, JSON.stringify(patients));
  }

  constructor(private _http: HttpClient,
              private _logger: LoggerService) {
  }

  public updatePatients(): Observable<Patient[]> {
    this._logger.log('Getting patients from server');
    return this._http.get<Patient[]>(
      `${environment.apiUrl}/patients/`
    ).pipe(
      map((patients: Patient[]) => {
        PatientService._updateLocalStorage(patients);
        return patients;
      })
    );
  }

  public getPatients(): Observable<Patient[]> {
    const localPatients = sessionStorage.getItem(patientsLSKey);

    if (!localPatients) {
      return this.updatePatients();
    } else {
      this._logger.log('Getting patients from local storage');
      return of(JSON.parse(localPatients));
    }
  }
}
