import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '@environments/environment';
import { map } from 'rxjs/operators';
import { LoggerService } from '@app/services/logger/logger.service';
import { Version } from '@app/model/Version';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class VersionService {

  private _environment: string = '';

  constructor(private _http: HttpClient,
              private _logger: LoggerService) {
  }

  public initEnvironment(): Observable<string> {
    return this._http.get<Version>(
      `${environment.apiUrl}/service/version`
    ).pipe(
      map((r: Object) => {
        const version = r as Version;
        this._environment = version.environment;
        return this._environment;
      })
    );
  }

  public getEnvironment(): string {
    return this._environment;
  }
}
