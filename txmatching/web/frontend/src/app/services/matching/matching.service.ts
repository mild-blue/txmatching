import { Injectable } from "@angular/core";
import { Configuration } from "@app/model/Configuration";
import { environment } from "@environments/environment";
import { HttpClient } from "@angular/common/http";
import { CalculatedMatchings } from "@app/model/Matching";
import { map } from "rxjs/operators";
import { CalculatedMatchingsGenerated, ConfigurationGenerated } from "@app/generated";
import { parseCalculatedMatchings } from "@app/parsers/matching.parsers";
import { ConfigurationId, PatientList } from "@app/model";
import { fromConfiguration } from "@app/parsers/to-generated/configuration.parsers";
import { firstValueFrom } from "rxjs";
import { ConfigurationService } from "../configuration/configuration.service";

@Injectable({
  providedIn: "root",
})
export class MatchingService {
  constructor(private _http: HttpClient, protected _configService: ConfigurationService) {}

  public async calculate(
    txmEventId: number,
    configId: number,
    patients: PatientList
  ): Promise<CalculatedMatchings> {
    return firstValueFrom(
      this._http
        .get<CalculatedMatchingsGenerated>(
          `${environment.apiUrl}/txm-event/${txmEventId}/matching/calculate-for-config/${configId}`
        )
        .pipe(map((_) => parseCalculatedMatchings(_, patients)))
    );
  }
}
