import { Component, OnInit } from '@angular/core';
import { PatientService } from '@app/services/patient/patient.service';
import { LoggerService } from '@app/services/logger/logger.service';
import { AlertService } from '@app/services/alert/alert.service';
import { AuthService } from '@app/services/auth/auth.service';
import { UploadDownloadStatus } from '@app/components/header/header.interface';
import { ConfigurationService } from '@app/services/configuration/configuration.service';
import { PatientList } from '@app/model/PatientList';
import { PatientPair } from '@app/model/PatientPair';
import { UploadService } from '@app/services/upload/upload.service';
import { Donor, DonorType } from '@app/model/Donor';
import { PatientPairItemComponent } from '@app/components/patient-pair-item/patient-pair-item.component';
import { PatientPairDetailComponent } from '@app/components/patient-pair-detail/patient-pair-detail.component';
import { PatientDonorItemComponent } from '@app/components/patient-donor-item/patient-donor-item.component';
import { PatientDonorDetailWrapperComponent } from '@app/components/patient-donor-detail-wrapper/patient-donor-detail-wrapper.component';
import { EventService } from '@app/services/event/event.service';
import { AbstractLoggedComponent } from '@app/pages/abstract-logged/abstract-logged.component';

@Component({
  selector: 'app-patients',
  templateUrl: './patients.component.html',
  styleUrls: ['./patients.component.scss']
})
export class PatientsComponent extends AbstractLoggedComponent implements OnInit {

  public patients?: PatientList;
  public pairs: PatientPair[] = [];
  public items: (Donor | PatientPair)[] = [];

  public loading: boolean = false;
  public error: boolean = false;
  public downloadStatus: UploadDownloadStatus = UploadDownloadStatus.hidden;
  public uploadStatus: UploadDownloadStatus = UploadDownloadStatus.enabled;
  public donorsCount: number = 0;
  public recipientCount: number = 0;
  public patientPopupOpened: boolean = false;

  constructor(private _uploadService: UploadService,
              _authService: AuthService,
              _alertService: AlertService,
              _configService: ConfigurationService,
              _eventService: EventService,
              _patientService: PatientService,
              _logger: LoggerService) {
    super(_authService, _alertService, _configService, _eventService, _patientService, _logger);
  }

  ngOnInit(): void {
    super.ngOnInit();

    this.loading = true;
    this._initAll().finally(() => this.loading = false);
  }

  private async _initAll(): Promise<void> {
    await this._initTxmEvents();
    await this._initPatientsAndConfiguration();
  }

  private async _initPatientsAndConfiguration(): Promise<void> {
    // We could possibly run _initPatientsWithStats and _initAppConfiguration in parallel (using Promise.all),
    // but we don't because due to the current BE limitations, it would not improve the performance significantly,
    // and could introduce some risks
    await this._initPatientsWithStats();
    await this._initAppConfiguration();
  }

  public async setDefaultTxmEvent(event_id: number): Promise<void> {
    this.loading = true;
    this.defaultTxmEvent = await this._eventService.setDefaultEvent(event_id);
    await this._initPatientsAndConfiguration();
    this.loading = false;
  }

  public uploadPatients(): void {
    if (!this.defaultTxmEvent) {
      this._logger.error('uploadPatients failed because defaultTxmEvent not set');
      return;
    }
    this._uploadService.uploadFile(
      this.defaultTxmEvent.id, 'Refresh patients', this._initPatientsWithStats.bind(this)
    );
  }

  public onNewPatientsAdded(): void {
    this.togglePatientPopup();
    this._initPatientsWithStats();
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
      if (donor.donor_type === DonorType.DONOR) {
        recipient = this.patients.recipients.find(r => r.db_id === donor.related_recipient_db_id);
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

  private async _initPatientsWithStats(): Promise<void> {
    // if not already loading before Promise.all
    let loadingWasSwitchedOn = false;
    if (!this.loading) {
      this.loading = true;
      loadingWasSwitchedOn = true;
    }

    // try getting patients
    try {
      await this._initPatients();
      if (!this.patients) {
        return;
      }
      this.donorsCount = this.patients.donors.length;
      this.recipientCount = this.patients.recipients.length;
      this._logger.log(`Got ${this.donorsCount + this.recipientCount} patients from server`, [this.patients]);

      // Init list items
      this._initItems();
    } finally {
      if (loadingWasSwitchedOn) {
        this.loading = false;
      }
    }
  }
}
