import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '@environments/environment';
import { first, map } from 'rxjs/operators';
import { LoggerService } from '@app/services/logger/logger.service';
import { PatientList } from '@app/model/PatientList';
import { Donor } from '@app/model/Donor';
import { Recipient } from '@app/model/Recipient';
import {
  DonorGenerated,
  DonorModelToUpdateGenerated,
  PatientsGenerated,
  PatientUploadSuccessResponseGenerated,
  RecipientGenerated,
  RecipientModelToUpdateGenerated
} from '@app/generated';
import { parseDonor, parsePatientList, parseRecipient } from '@app/parsers';
import { DonorEditable } from '@app/model/DonorEditable';
import { RecipientEditable } from '@app/model/RecipientEditable';
import { DonorModelPairIn } from '@app/services/patient/patient.service.interface';
import { fromDonorEditable } from '@app/parsers/to-generated/donor.parsers';
import { fromRecipientEditable } from '@app/parsers/to-generated/recipient.parsers';
import { Sex } from '@app/model';
import { Country } from '@app/model/enums/Country';
import { DonorType } from '@app/model/enums/DonorType';

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

  public async saveDonor(txmEventId: number, donorId: number, donorEditable: DonorEditable): Promise<Donor> {
    this._logger.log(`Saving donor ${donorId}`, [donorEditable]);
    const payload: DonorModelToUpdateGenerated = fromDonorEditable(donorEditable, donorId);
    this._logger.log('Sending payload', [payload]);

    return this._http.put<DonorGenerated>(
      `${environment.apiUrl}/txm-event/${txmEventId}/patients/donor`,
      payload
    ).pipe(
      first(),
      map(parseDonor)
    ).toPromise();
  }

  public async saveRecipient(txmEventId: number, recipientId: number, recipientEditable: RecipientEditable): Promise<Recipient> {
    this._logger.log(`Saving recipient ${recipientId}`, [recipientEditable]);
    const payload: RecipientModelToUpdateGenerated = fromRecipientEditable(recipientEditable, recipientId);
    this._logger.log('Sending payload', [payload]);

    return this._http.put<RecipientGenerated>(
      `${environment.apiUrl}/txm-event/${txmEventId}/patients/recipient`,
      payload
    ).pipe(
      first(),
      map(parseRecipient)
    ).toPromise();
  }

  public async addNewPair(txmEventId: number, donor: DonorEditable, recipient: RecipientEditable): Promise<PatientUploadSuccessResponseGenerated> {
    this._logger.log('Adding new pair', [donor, recipient]);

    const country = donor.country ?? Country.Cze; // Assume same country for the donor and the recipient
    const body: DonorModelPairIn = {
      country_code: country,
      donor: {
        medical_id: donor.medicalId,
        blood_group: donor.bloodGroup,
        hla_typing: donor.antigens,
        donor_type: donor.type,
        sex: donor.sex === Sex.NULL ? undefined : donor.sex,
        height: donor.height ? +donor.height : undefined,
        weight: donor.weight ? +donor.weight : undefined,
        year_of_birth: donor.yearOfBirth ? +donor.yearOfBirth : undefined
      }
    };

    if (donor.type.valueOf() === DonorType.DONOR.valueOf()) {
      body.donor.related_recipient_medical_id = recipient.medicalId;

      // Put cutoff value to antibodies
      recipient.antibodies.forEach(a => a.cutoff = recipient.antibodiesCutoff ? +recipient.antibodiesCutoff : 0);

      body.recipient = {
        acceptable_blood_groups: recipient.acceptableBloodGroups,
        blood_group: recipient.bloodGroup,
        height: recipient.height ? +recipient.height : undefined,
        hla_antibodies: recipient.antibodies,
        hla_typing: recipient.antigens,
        medical_id: recipient.medicalId,
        previous_transplants: recipient.previousTransplants ? +recipient.previousTransplants : undefined,
        sex: recipient.sex === Sex.NULL ? undefined : recipient.sex,
        waiting_since: this._formatDate(recipient.waitingSince),
        weight: recipient.weight ? +recipient.weight : undefined,
        year_of_birth: recipient.yearOfBirth ? +recipient.yearOfBirth : undefined
      };
    }

    return this._http.post<PatientUploadSuccessResponseGenerated>(
      `${environment.apiUrl}/txm-event/${txmEventId}/patients/pairs`,
      body
    ).pipe(first()).toPromise();
  }

  private _formatDate(date: Date): string {
    const y = date.getFullYear();
    const d = date.getDate();
    const m = date.getMonth();
    const month = m < 10 ? `0${m}` : 'm';

    return `${y}-${month}-${d}`;
  }
}
