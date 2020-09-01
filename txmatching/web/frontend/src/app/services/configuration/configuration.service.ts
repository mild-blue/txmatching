import { Injectable } from '@angular/core';
import { environment } from '@environments/environment';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { AppConfiguration } from '@app/model/Configuration';

@Injectable({
  providedIn: 'root'
})
export class ConfigurationService {

  constructor(private _http: HttpClient) {
  }

  public getConfiguration(): Observable<AppConfiguration> {
    return this._http.get<AppConfiguration>(
      `${environment.apiUrl}/configuration/`
    ).pipe();
  }
}
