import { Injectable } from '@angular/core';
import { AppConfiguration } from '@app/model/Configuration';
import { Observable } from 'rxjs';
import { environment } from '@environments/environment';
import { HttpClient } from '@angular/common/http';

@Injectable({
  providedIn: 'root'
})
export class MatchingService {

  constructor(private _http: HttpClient) {
  }

  public calculate(config: AppConfiguration): Observable<any> {
    return this._http.post<any>(
      `${environment.apiUrl}/matching/calculate-for-config`,
      config
    ).pipe();
  }
}
