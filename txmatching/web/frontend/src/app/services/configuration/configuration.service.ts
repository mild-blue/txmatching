import { Injectable } from "@angular/core";
import { environment } from "@environments/environment";
import { HttpClient } from "@angular/common/http";
import { Configuration } from "@app/model/Configuration";
import { map } from "rxjs/operators";
import { parseConfiguration, parseConfigurationId } from "@app/parsers/configuration.parsers";
import {
  ConfigurationGenerated,
  ConfigurationIdGenerated,
  IdentifierGenerated,
  SuccessGenerated,
} from "@app/generated";
import { firstValueFrom } from "rxjs";
import { ConfigurationId } from "@app/model";

@Injectable({
  providedIn: "root",
})
export class ConfigurationService {
  constructor(private _http: HttpClient) {}

  public async getConfiguration(txmEventId: number, configId: number | undefined): Promise<Configuration> {
    // TODO https://github.com/mild-blue/txmatching/issues/1191
    const configIdStr = configId !== undefined ? configId.toString() : "default";
    return firstValueFrom(
      this._http
        .get<ConfigurationGenerated>(`${environment.apiUrl}/txm-event/${txmEventId}/configuration/${configIdStr}`)
        .pipe(map(parseConfiguration))
    );
  }

  public async setConfigurationAsDefault(txmEventId: number, configId: number): Promise<boolean> {
    const payload: IdentifierGenerated = {
      id: configId,
    };
    return firstValueFrom(
      this._http
        .put<SuccessGenerated>(`${environment.apiUrl}/txm-event/${txmEventId}/configuration/set-default`, payload)
        .pipe(map((_) => _.success))
    );
  }

  public async findConfigurationId(txmEventId: number, payload: ConfigurationGenerated): Promise<ConfigurationId> {
    return firstValueFrom(
      this._http
        .post<ConfigurationIdGenerated>(
          `${environment.apiUrl}/txm-event/${txmEventId}/configuration/find-or-create-config`,
          payload
        )
        .pipe(map(parseConfigurationId))
    );
  }
}
