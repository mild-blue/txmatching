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
import { EventService } from '@app/services/event/event.service';
import { AbstractLoggedComponent } from '@app/pages/abstract-logged/abstract-logged.component';
import { Subscription } from 'rxjs';
import { PatientUploadSuccessResponseGenerated } from '@app/generated';
import { PatientPairToAdd } from '@app/services/patient/patient.service.interface';
import { DonorType } from '@app/model/enums/DonorType';
import { ReportService } from '@app/services/report/report.service';
import { UiInteractionsService } from '@app/services/ui-interactions/ui-interactions.service';

@Component({
  selector: 'app-patients',
  templateUrl: './patients.component.html',
  styleUrls: ['./patients.component.scss']
})
export class PatientsComponent extends AbstractLoggedComponent implements OnInit {

  private _deleteDonorSubscription?: Subscription;

  public patients?: PatientList;

  public items: (Donor | PatientPair)[] = [];
  public activeItem?: Donor | PatientPair;

  public error: boolean = false;
  public downloadMatchingStatus: UploadDownloadStatus = UploadDownloadStatus.hidden;
  public donorsCount: number = 0;
  public recipientCount: number = 0;
  public patientPopupOpened: boolean = false;

  public pairs: PatientPair[] = [];
  public donors: Donor[] = [];

  constructor(_reportService: ReportService,
              _authService: AuthService,
              _alertService: AlertService,
              _configService: ConfigurationService,
              _eventService: EventService,
              _patientService: PatientService,
              _logger: LoggerService,
              _uiInteractionsService: UiInteractionsService) {
    super(_reportService, _authService, _alertService, _configService, _eventService, _patientService, _logger, _uiInteractionsService);
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
      const response: PatientUploadSuccessResponseGenerated = await this._patientService.addNewPair(this.defaultTxmEvent.id, pair.donor, pair.recipient);
      this._alertService.success(`Successfully uploaded ${response.donors_uploaded} donor and ${response.recipients_uploaded} recipient${response.recipients_uploaded === 0 ? 's' : ''}`);
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
      this._alertService.error(`Error uploading patients: "${e.message || e}"`);
      this._logger.error(`Error uploading patients: "${e.message || e}"`);
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
    const pairs: PatientPair[] = [];
    const donors: Donor[] = [];
    for (const donor of this.patients.donors) {

      // try to find recipient
      let recipient;
      if (donor.donorType === DonorType.DONOR) {
        recipient = this.patients.recipients.find(r => r.dbId === donor.relatedRecipientDbId);
      }

      if (recipient) {
        // donor with valid recipient

        pairs.push({
          index: items.length + 1,
          d: donor,
          r: recipient
        });
      } else {
        // donor without recipient

        donors.push({
          ...donor,
          index: items.length + 1
        });
      }
    }

    this.items = [...items]; // make a copy, not a reference
    this.pairs = [...pairs];
    this.donors = [...donors];
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
}
