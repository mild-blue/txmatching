import { Injectable } from '@angular/core';
import { Patient, patientsLSKey } from '@app/model/Patient';
import { HttpClient } from '@angular/common/http';
import { environment } from '@environments/environment';
import { first } from 'rxjs/operators';
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

  public updatePatients(): Promise<Patient[]> {
    return new Promise((resolve, reject) => {
      this._http.get<Patient[]>(
        `${environment.apiUrl}/patients/`
      ).pipe(first())
      .subscribe((patients: Patient[]) => {
        this._logger.log('Got patients from server', [patients]);
        PatientService._updateLocalStorage(patients);
        resolve(patients);
      });
    });
  }

  public getPatients(): Patient[] {
    const localPatients = sessionStorage.getItem(patientsLSKey);
    return localPatients ? JSON.parse(localPatients) : [];
  }
}
