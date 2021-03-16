import { Injectable } from '@angular/core';
import { environment } from '@environments/environment';
import { HttpClient } from '@angular/common/http';
import { Configuration } from '@app/model/Configuration';
import { first, map } from 'rxjs/operators';
import { parseConfiguration } from '@app/parsers/configuration.parsers';
import { ConfigurationGenerated } from '@app/generated';

@Injectable({
  providedIn: 'root'
})
export class ConfigurationService {

  constructor(private _http: HttpClient) {
  }

  public async getConfiguration(txmEventId: number, configId: number | undefined): Promise<Configuration> {
    const configIdStr = configId !== undefined ? configId.toString() : 'default';
    return this._http.get<ConfigurationGenerated>(
      `${environment.apiUrl}/txm-event/${txmEventId}/configuration/${configIdStr}`
    ).pipe(
      first(),
      map(parseConfiguration)
    ).toPromise();
  }
}
