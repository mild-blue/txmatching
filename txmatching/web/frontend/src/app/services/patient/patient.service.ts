import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '@environments/environment';
import { first, map } from 'rxjs/operators';
import { LoggerService } from '@app/services/logger/logger.service';
import { PatientList } from '@app/model/PatientList';
import { Donor } from '@app/model/Donor';
import { Recipient } from '@app/model/Recipient';
import { Antibody } from '@app/model/Hla';
import { PatientsGenerated } from '@app/generated';
import { parsePatientList } from '@app/parsers';

@Injectable({
  providedIn: 'root'
})
export class PatientService {

  constructor(private _http: HttpClient,
              private _logger: LoggerService) {
  }

  public async getPatients(): Promise<PatientList> {
    return this._http.get<PatientsGenerated>(
      `${environment.apiUrl}/patients`
    ).pipe(first(), map(parsePatientList)).toPromise();
  }

  public async saveDonor(donor: Donor): Promise<Donor> {
    this._logger.log('Saving donor', [donor]);
    return this._http.put<Donor>(
      `${environment.apiUrl}/patients/donor`,
      {
        db_id: donor.db_id,
        hla_typing: {
          hla_types_list: donor.parameters.hla_typing.hla_types_list
        }
      }
    ).pipe(first()).toPromise();
  }

  public async saveRecipient(recipient: Recipient, antibodies: Antibody[]): Promise<Recipient> {
    this._logger.log('Saving recipient', [recipient]);
    return this._http.put<Recipient>(
      `${environment.apiUrl}/patients/recipient`,
      {
        db_id: recipient.db_id,
        acceptable_blood_groups: recipient.acceptable_blood_groups,
        hla_typing: {
          hla_types_list: recipient.parameters.hla_typing.hla_types_list
        },
        hla_antibodies: {
          hla_antibodies_list: antibodies
        },
        recipient_requirements: recipient.recipient_requirements
      }
    ).pipe(first()).toPromise();
  }
}
