import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '@environments/environment';
import { filter, map } from 'rxjs/operators';
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
import { BehaviorSubject, firstValueFrom, Observable } from 'rxjs';
import { DonorEditable } from '@app/model/DonorEditable';
import { RecipientEditable } from '@app/model/RecipientEditable';
import { fromDonorEditableToUpdateGenerated } from '@app/parsers/to-generated/donor.parsers';
import { fromRecipientEditableToUpdateGenerated } from '@app/parsers/to-generated/recipient.parsers';
import { fromPatientsEditableToInGenerated } from '@app/parsers/to-generated/patientPair.parsers';
import { ParsingIssue } from '@app/model/ParsingIssue';
import { parseParsingIssue } from '@app/parsers/parsingIssue.parsers';
import { parseParsingIssueConfirmation } from '@app/parsers/parsingIssueConfirmation.parsers';
import { ParsingIssueConfirmation } from '@app/model/ParsingIssueConfirmation';
import { ParsingIssueConfirmationComponent } from '@app/components/parsing-issue-confirmation/parsing-issue-confirmation.compontent';

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

  public async confirmWarning(txmEventId: number, warningId: number): Promise<ParsingIssueConfirmation> {
    // todo toto ma vraciat parsing issue confirmation
    this._logger.log(`Confirming warning ${warningId}`);
    let returnObject: ParsingIssueConfirmation =  await firstValueFrom(this._http.post(
      `${environment.apiUrl}/txm-event/${txmEventId}/patients/confirm-warning/${warningId}`,
      {}
    ));
    // // or
    // return this._http.post(
    //   `${environment.apiUrl}/txm-event/${txmEventId}/patients/confirm-warning/${warningId}`,
    //   {}
    // ).pipe{
    //   map(parseParsingIssueConfirmation);
    // }
  }

  public async getPatients(txmEventId: number, configId: number | undefined, includeAntibodiesRaw: boolean): Promise<PatientList> {
    const configIdStr = configId !== undefined ? configId.toString() : 'default';

    return firstValueFrom(this._http.get<PatientsGenerated>(
      `${environment.apiUrl}/txm-event/${txmEventId}/patients/configs/${configIdStr}${includeAntibodiesRaw ? '?include-antibodies-raw' : ''}`
    ).pipe(
      map(parsePatientList)
    ));
  }

  public async saveDonor(txmEventId: number, donorId: number, donorUpdateId: number, donorEditable: DonorEditable, configId: number | undefined): Promise<UpdatedDonor> {
    const configIdStr = configId !== undefined ? configId.toString() : 'default';

    this._logger.log(`Saving donor ${donorId}`, [donorEditable]);
    const payload: DonorModelToUpdateGenerated = fromDonorEditableToUpdateGenerated(donorEditable, donorId, donorUpdateId);
    this._logger.log('Sending payload', [payload]);

    return firstValueFrom(this._http.put<UpdatedDonorGenerated>(
      `${environment.apiUrl}/txm-event/${txmEventId}/patients/configs/${configIdStr}/donor`,
      payload
    ).pipe(
      map(parseUpdatedDonor)
    ));
  }

  public async saveRecipient(txmEventId: number, recipientId: number, recipientUpdateId: number, recipientEditable: RecipientEditable): Promise<UpdatedRecipient> {
    this._logger.log(`Saving recipient ${recipientId}`, [recipientEditable]);
    const payload: RecipientModelToUpdateGenerated = fromRecipientEditableToUpdateGenerated(recipientEditable, recipientId, recipientUpdateId);
    this._logger.log('Sending payload', [payload]);

    return firstValueFrom(this._http.put<UpdatedRecipientGenerated>(
      `${environment.apiUrl}/txm-event/${txmEventId}/patients/recipient`,
      payload
    ).pipe(
      map(parseUpdatedRecipient)
    ));
  }

  public async addNewPair(txmEventId: number, donor: DonorEditable, recipient: RecipientEditable): Promise<ParsingIssue[]> {
    this._logger.log('Adding new pair', [donor, recipient]);

    const payload: DonorModelPairInGenerated = fromPatientsEditableToInGenerated(
      donor, recipient
    );

    return firstValueFrom(this._http.post<PatientUploadSuccessResponseGenerated>(
      `${environment.apiUrl}/txm-event/${txmEventId}/patients/pairs`,
      payload
    ).pipe(
      map(_ => _.parsing_issues.map(parseParsingIssue))
    ));
  }

  public async deleteDonor(txmEventId: number, donorDbId: number): Promise<void> {
    this._logger.log(`Deleting donor ${donorDbId}`);
    await firstValueFrom(this._http.delete(
      `${environment.apiUrl}/txm-event/${txmEventId}/patients/pairs/${donorDbId}`
    ));
    this._deletedDonorDbIdSubject.next(donorDbId);
  }
}
