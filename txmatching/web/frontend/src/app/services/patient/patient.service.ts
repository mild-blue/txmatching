import { Injectable } from '@angular/core';
import { Observable, of } from 'rxjs';
import { Patient, patientsLSKey } from '@app/model/Patient';
import { HttpClient } from '@angular/common/http';
import { environment } from '@environments/environment';
import { map } from 'rxjs/operators';

@Injectable({
  providedIn: 'root'
})
export class PatientService {

  private static _updateLocalStorage(patients: Patient[]) {
    localStorage.removeItem(patientsLSKey);
    localStorage.setItem(patientsLSKey, JSON.stringify(patients));
  }

  constructor(private _http: HttpClient) {
  }

  public updatePatients(): Observable<Patient[]> {
    console.log('Getting patients from server');
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
    const localPatients = localStorage.getItem(patientsLSKey);

    if (!localPatients) {
      return this.updatePatients();
    }

    console.log('Getting patients from local storage');
    return of(JSON.parse(localPatients));
  }
}
