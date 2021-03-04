import { Injectable } from '@angular/core';
import { environment } from '@environments/environment';
import { HttpClient } from '@angular/common/http';
import { AppConfiguration } from '@app/model/Configuration';
import { first, map } from 'rxjs/operators';
import { parseAppConfiguration } from '@app/parsers/configuration.parsers';
import { ConfigurationGenerated } from '@app/generated';

@Injectable({
  providedIn: 'root'
})
export class ConfigurationService {

  constructor(private _http: HttpClient) {
  }

  public async getAppConfiguration(txmEventId: number): Promise<AppConfiguration> {
    return this._http.get<ConfigurationGenerated>(
      `${environment.apiUrl}/txm-event/${txmEventId}/configuration`
    ).pipe(
      first(),
      map(parseAppConfiguration)
    ).toPromise();
  }
}
