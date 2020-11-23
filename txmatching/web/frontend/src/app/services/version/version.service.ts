import {Injectable} from '@angular/core';
import {HttpClient} from '@angular/common/http';
import {environment} from '@environments/environment';
import {first} from 'rxjs/operators';
import {LoggerService} from '@app/services/logger/logger.service';
import {Version} from "../../model/Version";

@Injectable({
  providedIn: 'root'
})
export class VersionService {

  constructor(
    private _http: HttpClient,
              private _logger: LoggerService
  ) {
  }

  public async getEnvironment(): Promise<Version> {
    return this._http.get<Version>(
      `${environment.apiUrl}/service/version`
    ).pipe(first()).toPromise();
  }
}
