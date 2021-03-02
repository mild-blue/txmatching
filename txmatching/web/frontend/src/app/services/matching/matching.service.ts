import { Injectable } from '@angular/core';
import { AppConfiguration } from '@app/model/Configuration';
import { environment } from '@environments/environment';
import { HttpClient } from '@angular/common/http';
import { CalculatedMatchings } from '@app/model/Matching';
import { first, map } from 'rxjs/operators';
import { CalculatedMatchingsGenerated, ConfigurationGenerated } from '@app/generated';
import { parseCalculatedMatchings } from '@app/parsers/matching.parsers';
import { PatientList } from '@app/model';
import { fromAppConfiguration } from '@app/parsers/to-generated/configuration.parsers';

@Injectable({
  providedIn: 'root'
})
export class MatchingService {

  constructor(private _http: HttpClient) {
  }

  public async calculate(txmEventId: number, config: AppConfiguration, patients: PatientList): Promise<CalculatedMatchings> {
    const payload: ConfigurationGenerated = fromAppConfiguration(config);
    return this._http.post<CalculatedMatchingsGenerated>(
      `${environment.apiUrl}/txm-event/${txmEventId}/matching/calculate-for-config`,
      payload
    ).pipe(
      first(),
      map(_ => parseCalculatedMatchings(_, patients))
    ).toPromise();
  }
}
