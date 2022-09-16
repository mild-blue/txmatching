import { Injectable } from "@angular/core";
import { HttpClient } from "@angular/common/http";
import { environment } from "@environments/environment";
import { map } from "rxjs/operators";
import { LoggerService } from "@app/services/logger/logger.service";
import { Version } from "@app/model/Version";
import { Observable } from "rxjs";
import { VersionGenerated } from "@app/generated";
import { parseVersion } from "@app/parsers/version.parsers";

@Injectable({
  providedIn: "root",
})
export class VersionService {
  private _version?: Version;

  constructor(private _http: HttpClient, private _logger: LoggerService) {}

  public initEnvironment(): Observable<string> {
    return this._http.get<VersionGenerated>(`${environment.apiUrl}/service/version`).pipe(
      map(parseVersion),
      map((version: Version) => {
        this._version = version;
        return version.environment;
      })
    );
  }

  public initColourScheme(): Observable<string> {
    return this._http.get<VersionGenerated>(`${environment.apiUrl}/service/version`).pipe(
      map(parseVersion),
      map((version: Version) => {
        this._version = version;
        return version.colour_scheme;
      })
    );
  }

  public getColourScheme(): string {
    return this._version?.colour_scheme || "";
  }

  public getEnvironment(): string {
    return this._version?.environment || "";
  }

  public getVersion(): Version | undefined {
    return this._version;
  }
}
