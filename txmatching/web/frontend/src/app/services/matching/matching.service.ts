import { Injectable } from '@angular/core';
import { AppConfiguration } from '@app/model/Configuration';
import { Observable } from 'rxjs';
import { environment } from '@environments/environment';
import { HttpClient } from '@angular/common/http';
import { Matching } from '@app/model/Matching';
import { first } from 'rxjs/operators';

@Injectable({
  providedIn: 'root'
})
export class MatchingService {

  constructor(private _http: HttpClient) {
  }

  public calculate(config: AppConfiguration): Observable<Matching[]> {
    return this._http.post<Matching[]>(
      `${environment.apiUrl}/matching/calculate-for-config`,
      config
    ).pipe(first());
  }
}
