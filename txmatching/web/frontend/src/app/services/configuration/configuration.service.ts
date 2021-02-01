import { Injectable } from '@angular/core';
import { environment } from '@environments/environment';
import { HttpClient } from '@angular/common/http';
import { AppConfiguration } from '@app/model/Configuration';

@Injectable({
  providedIn: 'root'
})
export class ConfigurationService {

  constructor(private _http: HttpClient) {
  }

  public async getConfiguration(txmEventId: number): Promise<AppConfiguration> {
    // TODO: https://github.com/mild-blue/txmatching/issues/401 Create parser and use generated model
    return this._http.get<AppConfiguration>(
      `${environment.apiUrl}/txm-event/${txmEventId}/configuration`
    ).pipe().toPromise();
  }
}
