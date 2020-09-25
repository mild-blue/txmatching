import { Injectable } from '@angular/core';
import { PatientList, patientsLSKey } from '@app/model/Patient';
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
}
