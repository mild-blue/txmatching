import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '@environments/environment';
import { first, map } from 'rxjs/operators';
import { LoggerService } from '@app/services/logger/logger.service';
import { PatientList } from '@app/model/PatientList';
import { Donor } from '@app/model/Donor';
import { Recipient } from '@app/model/Recipient';
import { Antibody } from '@app/model/Hla';
import {
  BloodGroupEnumGenerated,
  DonorGenerated,
  DonorModelToUpdateGenerated,
  PatientsGenerated,
  RecipientGenerated,
  RecipientModelToUpdateGenerated,
  SexEnumGenerated
} from '@app/generated';
import { parseDonor, parsePatientList, parseRecipient } from '@app/parsers';

@Injectable({
  providedIn: 'root'
})
export class PatientService {

  constructor(private _http: HttpClient,
              private _logger: LoggerService) {
  }

  public async getPatients(txmEventId: number): Promise<PatientList> {
    return this._http.get<PatientsGenerated>(
      `${environment.apiUrl}/txm-event/${txmEventId}/patients`
    ).pipe(
      first(),
      map(parsePatientList)
    ).toPromise();
  }

  public saveDonor(txmEventId: number, donor: Donor): Promise<Donor> {
    this._logger.log('Saving donor', [donor]);
    const payload: DonorModelToUpdateGenerated = {
      db_id: donor.db_id,
      blood_group: BloodGroupEnumGenerated['A'], // TODOO
      hla_typing: {
        hla_types_list: donor.parameters.hla_typing.hla_types_list
      },
      sex: SexEnumGenerated['M'], // TODOO
      height: donor.parameters.height,
      weight: donor.parameters.weight,
      year_of_birth: donor.parameters.year_of_birth,

      active: donor.active
    };
    return this._http.put<DonorGenerated>(
      `${environment.apiUrl}/txm-event/${txmEventId}/patients/donor`,
      payload
    ).pipe(
      first(),
      map(parseDonor)
    ).toPromise();
  }

  public saveRecipient(txmEventId: number, recipient: Recipient, antibodies: Antibody[]): Promise<Recipient> {
    this._logger.log('Saving recipient', [recipient]);
    const payload: RecipientModelToUpdateGenerated = {
      db_id: recipient.db_id,
      blood_group: BloodGroupEnumGenerated['A'], // TODOO
      hla_typing: {
        hla_types_list: recipient.parameters.hla_typing.hla_types_list
      },
      sex: SexEnumGenerated['M'], // TODOO
      height: recipient.parameters.height,
      weight: recipient.parameters.weight,
      year_of_birth: recipient.parameters.year_of_birth,

      acceptable_blood_groups: [BloodGroupEnumGenerated['A'], BloodGroupEnumGenerated['B']], // TODOO
      hla_antibodies: {
        hla_antibodies_list: antibodies
      },
      recipient_requirements: recipient.recipient_requirements,
      cutoff: 42, // TODOO
    };
    return this._http.put<RecipientGenerated>(
      `${environment.apiUrl}/txm-event/${txmEventId}/patients/recipient`,
      payload
    ).pipe(
      first(),
      map(parseRecipient)
    ).toPromise();
  }
}
