import { Injectable } from '@angular/core';
import { AppConfiguration } from '@app/model/Configuration';
import { environment } from '@environments/environment';
import { HttpClient } from '@angular/common/http';
import {CalculatedMatchings, Matching} from '@app/model/Matching';
import { first } from 'rxjs/operators';

@Injectable({
  providedIn: 'root'
})
export class MatchingService {

  constructor(private _http: HttpClient) {
  }

  public async calculate(config: AppConfiguration): Promise<CalculatedMatchings> {
    return this._http.post<CalculatedMatchings>(
      `${environment.apiUrl}/matching/calculate-for-config`,
      config
    ).pipe(first()).toPromise();
  }
}
