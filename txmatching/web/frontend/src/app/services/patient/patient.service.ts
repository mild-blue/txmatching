import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '@environments/environment';
import { filter, first, map } from 'rxjs/operators';
import { LoggerService } from '@app/services/logger/logger.service';
import { PatientList } from '@app/model/PatientList';
import { UpdatedDonor } from '@app/model/Donor';
import { UpdatedRecipient } from '@app/model/Recipient';
import {
  DonorModelPairInGenerated,
  DonorModelToUpdateGenerated,
  PatientsGenerated,
  PatientUploadSuccessResponseGenerated,
  RecipientModelToUpdateGenerated,
  UpdatedDonorGenerated,
  UpdatedRecipientGenerated
} from '@app/generated';
import { parsePatientList, parseUpdatedDonor, parseUpdatedRecipient } from '@app/parsers';
import { BehaviorSubject, Observable } from 'rxjs';
import { DonorEditable } from '@app/model/DonorEditable';
import { RecipientEditable } from '@app/model/RecipientEditable';
import { fromDonorEditableToUpdateGenerated } from '@app/parsers/to-generated/donor.parsers';
import { fromRecipientEditableToUpdateGenerated } from '@app/parsers/to-generated/recipient.parsers';
import { fromPatientsEditableToInGenerated } from '@app/parsers/to-generated/patientPair.parsers';
import { ParsingError } from '@app/model/ParsingError';
import { parseParsingError } from '@app/parsers/parsingError.parsers';

@Injectable({
  providedIn: 'root'
})
export class PatientService {

  private _deletedDonorDbIdSubject: BehaviorSubject<number> = new BehaviorSubject<number>(-1);

  constructor(private _http: HttpClient,
              private _logger: LoggerService) {
  }

  public onDeleteDonor(): Observable<number> {
    return this._deletedDonorDbIdSubject.asObservable().pipe(filter(dbId => dbId !== -1));
  }

  public async getPatients(txmEventId: number, configId: number | undefined, includeAntibodiesRaw: boolean): Promise<PatientList> {
    const configIdStr = configId !== undefined ? configId.toString() : 'default';

    // TODO: use observables https://github.com/mild-blue/txmatching/issues/674
    // @ts-ignore
    return this._http.get<PatientsGenerated>(
      `${environment.apiUrl}/txm-event/${txmEventId}/patients/configs/${configIdStr}${includeAntibodiesRaw ? '?include-antibodies-raw' : ''}`
    ).pipe(
      first(),
      map(parsePatientList)
    ).toPromise();
  }

  public async saveDonor(txmEventId: number, donorId: number, donorUpdateId: number, donorEditable: DonorEditable, configId: number | undefined): Promise<UpdatedDonor> {
    const configIdStr = configId !== undefined ? configId.toString() : 'default';

    this._logger.log(`Saving donor ${donorId}`, [donorEditable]);
    const payload: DonorModelToUpdateGenerated = fromDonorEditableToUpdateGenerated(donorEditable, donorId, donorUpdateId);
    this._logger.log('Sending payload', [payload]);

    // TODO: use observables https://github.com/mild-blue/txmatching/issues/674
    // @ts-ignore
    return this._http.put<UpdatedDonorGenerated>(
      `${environment.apiUrl}/txm-event/${txmEventId}/patients/configs/${configIdStr}/donor`,
      payload
    ).pipe(
      first(),
      map(parseUpdatedDonor)
    ).toPromise();
  }

  public async saveRecipient(txmEventId: number, recipientId: number, recipientUpdateId: number, recipientEditable: RecipientEditable): Promise<UpdatedRecipient> {
    this._logger.log(`Saving recipient ${recipientId}`, [recipientEditable]);
    const payload: RecipientModelToUpdateGenerated = fromRecipientEditableToUpdateGenerated(recipientEditable, recipientId, recipientUpdateId);
    this._logger.log('Sending payload', [payload]);

    // TODO: use observables https://github.com/mild-blue/txmatching/issues/674
    // @ts-ignore
    return this._http.put<UpdatedRecipientGenerated>(
      `${environment.apiUrl}/txm-event/${txmEventId}/patients/recipient`,
      payload
    ).pipe(
      first(),
      map(parseUpdatedRecipient)
    ).toPromise();
  }

  public async addNewPair(txmEventId: number, donor: DonorEditable, recipient: RecipientEditable): Promise<ParsingError[]> {
    this._logger.log('Adding new pair', [donor, recipient]);

    const payload: DonorModelPairInGenerated = fromPatientsEditableToInGenerated(
      donor, recipient
    );

    // TODO: use observables https://github.com/mild-blue/txmatching/issues/674
    // @ts-ignore
    return this._http.post<PatientUploadSuccessResponseGenerated>(
      `${environment.apiUrl}/txm-event/${txmEventId}/patients/pairs`,
      payload
    ).pipe(
      first(),
      map(_ => _.parsing_errors.map(parseParsingError))
    ).toPromise();
  }

  public async deleteDonor(txmEventId: number, donorDbId: number): Promise<void> {
    this._logger.log(`Deleting donor ${donorDbId}`);
    await this._http.delete(
      `${environment.apiUrl}/txm-event/${txmEventId}/patients/pairs/${donorDbId}`
    ).pipe(first()).toPromise();
    this._deletedDonorDbIdSubject.next(donorDbId);
  }
}
