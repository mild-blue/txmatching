import { Component, OnInit } from '@angular/core';
import { PatientService } from '@app/services/patient/patient.service';
import { LoggerService } from '@app/services/logger/logger.service';
import { AlertService } from '@app/services/alert/alert.service';
import { AuthService } from '@app/services/auth/auth.service';
import { UploadDownloadStatus } from '@app/components/header/header.interface';
import { ConfigurationService } from '@app/services/configuration/configuration.service';
import { PatientList } from '@app/model/PatientList';
import { PatientPair } from '@app/model/PatientPair';
import { Donor } from '@app/model/Donor';
import { PatientPairItemComponent } from '@app/components/patient-pair-item/patient-pair-item.component';
import { PatientPairDetailComponent } from '@app/components/patient-pair-detail/patient-pair-detail.component';
import { PatientDonorItemComponent } from '@app/components/patient-donor-item/patient-donor-item.component';
import { PatientDonorDetailWrapperComponent } from '@app/components/patient-donor-detail-wrapper/patient-donor-detail-wrapper.component';
import { EventService } from '@app/services/event/event.service';
import { AbstractLoggedComponent } from '@app/pages/abstract-logged/abstract-logged.component';
import { Subscription } from 'rxjs';
import { TxmEventStateGenerated } from '@app/generated';
import { PatientPairToAdd } from '@app/services/patient/patient.service.interface';
import { DonorType } from '@app/model/enums/DonorType';
import { ReportService } from '@app/services/report/report.service';
import { ParsingIssue } from '@app/model/ParsingIssue';
import { getErrorMessage } from '@app/helpers/error';

@Component({
  selector: 'app-patients',
  templateUrl: './patients.component.html',
  styleUrls: ['./patients.component.scss']
})
export class PatientsComponent extends AbstractLoggedComponent implements OnInit {

  private _deleteDonorSubscription?: Subscription;

  public patients?: PatientList;
  public pairs: PatientPair[] = [];
  public items: (Donor | PatientPair)[] = [];
  public activeItem?: Donor | PatientPair;

  public error: boolean = false;
  public downloadMatchingStatus: UploadDownloadStatus = UploadDownloadStatus.hidden;
  public donorsCount: number = 0;
  public recipientCount: number = 0;
  public patientPopupOpened: boolean = false;

  constructor(_reportService: ReportService,
              _authService: AuthService,
              _alertService: AlertService,
              _configService: ConfigurationService,
              _eventService: EventService,
              _patientService: PatientService,
              _logger: LoggerService) {
    super(_reportService, _authService, _alertService, _configService, _eventService, _patientService, _logger);
  }

  ngOnInit(): void {
    super.ngOnInit();

    this.loading = true;

    this._deleteDonorSubscription = this._patientService.onDeleteDonor().subscribe((donorDbId) => {
      this._alertService.success('Patients were deleted');
      this._initPatientsWithStats();
    });

    this._initAll().finally(() => this.loading = false);
  }

  ngOnDestroy(): void {
    this._deleteDonorSubscription?.unsubscribe();
  }

  private async _initAll(): Promise<void> {
    await this._initTxmEvents();
    await this._initPatientsAndConfiguration();
  }

  private async _initPatientsAndConfiguration(): Promise<void> {
    // We could possibly run _initPatientsWithStats and _initConfiguration in parallel (using Promise.all),
    // but we don't because due to the current BE limitations, it would not improve the performance significantly,
    // and could introduce some risks
    await this._initPatientsWithStats();
    await this._initConfiguration();
  }

  public async setDefaultTxmEvent(eventId: number): Promise<void> {
    this.loading = true;
    this.defaultTxmEvent = await this._eventService.setDefaultEvent(eventId);
    await this._initPatientsAndConfiguration();
    this.loading = false;
  }

  public async addPatientPair(pair: PatientPairToAdd): Promise<void> {
    if (!this.defaultTxmEvent) {
      this._logger.error('uploadPatients failed because defaultTxmEvent not set');
      return;
    }

    try {
      const parsingIssues: ParsingIssue[] = await this._patientService.addNewPair(this.defaultTxmEvent.id, pair.donor, pair.recipient);

      if (parsingIssues.length === 0) {
        this._alertService.success('Patients were successfully added');
      } else {
        this._alertService.infoWithParsingIssues(
          'Patients were added but some parsing issues or warnings occurred. ' +
          'You can modify the patient to fix the issues or contact us if the issues are not clear on info@mild.blue or +420 723 927 536.',
          parsingIssues
        );
        this._logger.log('Parsing issues', parsingIssues);
      }

      this.togglePatientPopup();
      await this._initPatientsWithStats();

      // Make added pair active
      const addedDonorMedicalId = pair.donor.medicalId;
      this.activeItem = this.items.find(item => {
        if (('donorType' in item && item.medicalId === addedDonorMedicalId) ||
          ('d' in item && item.d?.medicalId === addedDonorMedicalId)) {
          return item;
        }
        return undefined;
      });
    } catch (e) {
      this._alertService.error(`Error uploading patients: "${getErrorMessage(e)}"`);
      this._logger.error(`Error uploading patients: "${getErrorMessage(e)}"`);
    }
  }

  public togglePatientPopup(): void {
    this.patientPopupOpened = !this.patientPopupOpened;
  }

  private _initItems(): void {
    if (!this.patients) {
      this._logger.error('Items init failed because patients not set');
      return;
    }

    const items: (Donor | PatientPair)[] = [];
    for (const donor of this.patients.donors) {

      // try to find recipient
      let recipient;
      if (donor.donorType === DonorType.DONOR) {
        recipient = this.patients.recipients.find(r => r.dbId === donor.relatedRecipientDbId);
      }

      if (recipient) {
        // donor with valid recipient
        items.push({
          index: items.length + 1,
          d: donor,
          r: recipient,
          itemComponent: PatientPairItemComponent,
          detailComponent: PatientPairDetailComponent
        });
      } else {
        // donor without recipient
        items.push({
          ...donor,
          index: items.length + 1,
          itemComponent: PatientDonorItemComponent,
          detailComponent: PatientDonorDetailWrapperComponent
        });
      }
    }

    this.items = [...items]; // make a copy, not a reference
  }

  private _initPatientStatsAndItems(): void {
    if (!this.patients) {
      this._logger.error('_initPatientStatsAndItems failed because patients not set');
      return;
    }
    this.donorsCount = this.patients.donors.length;
    this.recipientCount = this.patients.recipients.length;

    // Init list items
    this._initItems();
  }

  private async _initPatientsWithStats(): Promise<void> {
    // if not already loading before Promise.all
    let loadingWasSwitchedOn = false;
    if (!this.loading) {
      this.loading = true;
      loadingWasSwitchedOn = true;
    }

    // try getting patients
    try {
      await this._initPatients(true);
      this._initPatientStatsAndItems();
      this._logger.log(`Got ${this.donorsCount + this.recipientCount} patients from server`, [this.patients]);
    } finally {
      if (loadingWasSwitchedOn) {
        this.loading = false;
      }
    }
  }

  get canModifyPatients(): boolean {
    return this.defaultTxmEvent?.state === TxmEventStateGenerated.Open;
  }
}
