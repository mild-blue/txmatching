import { Injectable } from '@angular/core';
import { AppConfiguration } from '@app/model/Configuration';
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

  public async calculate(config: AppConfiguration): Promise<Matching[]> {
    return this._http.post<Matching[]>(
      `${environment.apiUrl}/matching/calclate-for-config`,
      config
    ).pipe(first()).toPromise();
  }
}
