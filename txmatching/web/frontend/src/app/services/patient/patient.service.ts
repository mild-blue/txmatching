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

  public async updatePatients(): Promise<Patient[]> {
    const patients: Patient[] = await this._http.get<Patient[]>(
      `${environment.apiUrl}/patients/`
    ).pipe(first()).toPromise();

    PatientService._updateLocalStorage(patients);
    return patients;
  }

  public getPatients(): Patient[] {
    const localPatients = sessionStorage.getItem(patientsLSKey);
    return localPatients ? JSON.parse(localPatients) : [];
  }
}
