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

  private environment: string | null = null;

  constructor(
    private _http: HttpClient,
    private _logger: LoggerService
  ) {
  }

  public getEnvironment(): string | null {
    if (this.environment) {
      return this.environment
    }

    const promise = this._http.get<Version>(
      `${environment.apiUrl}/service/version`
    ).pipe(first()).toPromise();

    promise.then((value: Version) => {
      this.environment = value.environment
    }).catch((reason: any) => {
      this._logger.error('Could not set theme.', reason)
    })
    return this.environment
  }
}
