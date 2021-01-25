import { Injectable } from '@angular/core';
import { AppConfiguration } from '@app/model/Configuration';
import { environment } from '@environments/environment';
import { HttpClient } from '@angular/common/http';
import {CalculatedMatchings, Matching} from '@app/model/Matching';
import { first, map } from 'rxjs/operators';
import { CalculatedMatchingsGenerated } from '@app/generated';
import { parseCalculatedMatchings } from '@app/parsers/matching.parsers';
import { PatientList } from '@app/model';

@Injectable({
  providedIn: 'root'
})
export class MatchingService {

  constructor(private _http: HttpClient) {
  }

  public async calculate(config: AppConfiguration, patients: PatientList): Promise<CalculatedMatchings> {
    return this._http.post<CalculatedMatchingsGenerated>(
      `${environment.apiUrl}/matching/calculate-for-config`,
      config
    ).pipe(
      first(),
      map(_ => parseCalculatedMatchings(_, patients))
    ).toPromise();
  }
}
