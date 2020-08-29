import { Injectable } from '@angular/core';
import { environment } from '@environments/environment';
import { HttpClient } from '@angular/common/http';
import { Subscription } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class ConfigurationService {

  constructor(private _http: HttpClient) {
  }

  public getConfiguration(): Subscription {
    console.log('getting config');
    return this._http.get(
      `${environment.apiUrl}/configuration/`
    )
    .subscribe(
      data => console.log(data),
      err => console.log(err)
    );
  }
}
