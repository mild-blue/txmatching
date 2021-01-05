import { Component, OnInit } from '@angular/core';
import { PatientService } from '@app/services/patient/patient.service';
import { LoggerService } from '@app/services/logger/logger.service';
import { AlertService } from '@app/services/alert/alert.service';
import { User } from '@app/model/User';
import { AuthService } from '@app/services/auth/auth.service';
import { UploadDownloadStatus } from '@app/components/header/header.interface';
import { ConfigurationService } from '@app/services/configuration/configuration.service';
import { AppConfiguration } from '@app/model/Configuration';
import { PatientList } from '@app/model/PatientList';
import { PatientPair } from '@app/model/PatientPair';
import { UploadService } from '@app/services/upload/upload.service';
import { Donor, DonorType } from '@app/model/Donor';
import { PatientPairItemComponent } from '@app/components/patient-pair-item/patient-pair-item.component';
import { PatientPairDetailComponent } from '@app/components/patient-pair-detail/patient-pair-detail.component';
import { PatientDonorItemComponent } from '@app/components/patient-donor-item/patient-donor-item.component';
import { PatientDonorDetailComponent } from '@app/components/patient-donor-detail/patient-donor-detail.component';

@Component({
  selector: 'app-patients',
  templateUrl: './patients.component.html',
  styleUrls: ['./patients.component.scss']
})
export class PatientsComponent implements OnInit {

  public patients?: PatientList;
  public pairs: PatientPair[] = [];
  public items: (Donor | PatientPair)[] = [];

  public loading: boolean = false;
  public error: boolean = false;
  public downloadStatus: UploadDownloadStatus = UploadDownloadStatus.hidden;
  public uploadStatus: UploadDownloadStatus = UploadDownloadStatus.enabled;

  public user?: User;

  public configuration?: AppConfiguration;

  constructor(private _authService: AuthService,
              private _alertService: AlertService,
              private _configService: ConfigurationService,
              private _patientService: PatientService,
              private _uploadService: UploadService,
              private _logger: LoggerService) {
  }

  ngOnInit(): void {
    this.user = this._authService.currentUserValue;

    // init config and patients
    this.loading = true;
    Promise.all([this._initConfiguration(), this._initPatients()]).finally(() => this.loading = false);
  }

  public uploadPatients(): void {
    this._uploadService.uploadFile('Refresh patients', this._initPatients.bind(this));
  }

  private _initItems(): void {
    if (!this.patients) {
      return;
    }

    const items: (Donor | PatientPair)[] = [];
    for (const donor of this.patients.donors) {
      if (donor.donor_type === DonorType.DONOR) {
        // if donor with recipient

        // find recipient
        const recipient = this.patients.recipients.find(r => r.db_id === donor.related_recipient_db_id);
        if (!recipient) {
          continue;
        }

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
          detailComponent: PatientDonorDetailComponent
        });
      }
    }

    this.items = [...items]; // make a copy, not a reference
  }

  private async _initPatients(): Promise<void> {

    // if not already loading before Promise.all
    let loadingWasSwitchedOn = false;
    if (!this.loading) {
      this.loading = true;
      loadingWasSwitchedOn = true;
    }

    // try getting patients
    try {
      this.patients = await this._patientService.getPatients();
      this._logger.log('Got patients from server', [this.patients]);

      // Init list items
      this._initItems();
    } catch (e) {
      this._alertService.error(`Error loading patients: "${e.message || e}"`);
      this._logger.error(`Error loading patients: "${e.message || e}"`);
    } finally {
      this._logger.log('End of loading patients');

      // So we do not switch off loading called before Promise.all
      if (loadingWasSwitchedOn) {
        this.loading = false;
      }
    }
  }

  private async _initConfiguration(): Promise<void> {
    try {
      this.configuration = await this._configService.getConfiguration();
      this._logger.log('Got config from server', [this.configuration]);
    } catch (e) {
      this._alertService.error(`Error loading configuration: "${e.message || e}"`);
      this._logger.error(`Error loading configuration: "${e.message || e}"`);
    }
  }
}
