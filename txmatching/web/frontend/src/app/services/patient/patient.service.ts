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
import { Observable, Subject } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class PatientService {

  private _deleteDonorSubject: Subject<number> = new Subject<number>();

  constructor(private _http: HttpClient,
              private _logger: LoggerService) {
  }

  public onDeleteDonor(): Observable<number> {
    return this._deleteDonorSubject.asObservable();
  }

  public async getPatients(txmEventId: number): Promise<PatientList> {
    return this._http.get<PatientsGenerated>(
      `${environment.apiUrl}/txm-event/${txmEventId}/patients`
    ).pipe(
      first(),
      map(parsePatientList)
    ).toPromise();
  }

  public async saveDonor(txmEventId: number, donor: Donor): Promise<Donor> {
    this._logger.log('Saving donor', [donor]);
    return this._http.put<Donor>(
      `${environment.apiUrl}/txm-event/${txmEventId}/patients/donor`,
      {
        db_id: donor.db_id,
        hla_typing: {
          hla_types_list: donor.parameters.hla_typing.hla_types_list
        },
        active: donor.active
      }
    ).pipe(first()).toPromise();
  }

  public async saveRecipient(txmEventId: number, recipient: Recipient, antibodies: Antibody[]): Promise<Recipient> {
    this._logger.log('Saving recipient', [recipient]);
    return this._http.put<Recipient>(
      `${environment.apiUrl}/txm-event/${txmEventId}/patients/recipient`,
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

  public async deleteDonor(txmEventId: number, donorDbId: number): Promise<void> {
    this._logger.log(`Deleting donor ${donorDbId}`);
    await this._http.delete(
      `${environment.apiUrl}/txm-event/${txmEventId}/patients/pairs/${donorDbId}`
    ).pipe(first()).toPromise();
    this._deleteDonorSubject.next(donorDbId);
  }
}
