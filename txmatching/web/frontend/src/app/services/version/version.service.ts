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

  private _version?: Version;

  constructor(private _http: HttpClient,
              private _logger: LoggerService) {
  }

  public initEnvironment(): Observable<string> {
    // TODO: Create parser and use generated model
    return this._http.get<Version>(
      `${environment.apiUrl}/service/version`
    ).pipe(
      map((r: Object) => {
        const version = r as Version;
        this._version = version;
        return version.environment;
      })
    );
  }

  public getEnvironment(): string {
    return this._version?.environment || '';
  }

  public getVersion(): Version | undefined {
    return this._version;
  }
}
