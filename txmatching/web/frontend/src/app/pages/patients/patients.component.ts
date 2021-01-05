import { Component, OnInit } from '@angular/core';
import { PatientService } from '@app/services/patient/patient.service';
import { ListItem } from '@app/components/list-item/list-item.interface';
import { PatientListFilter, patientListFilters, PatientListFilterType } from '@app/pages/patients/patients.interface';
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

@Component({
  selector: 'app-patients',
  templateUrl: './patients.component.html',
  styleUrls: ['./patients.component.scss']
})
export class PatientsComponent implements OnInit {

  public activeListFilter?: PatientListFilter;
  public tabs: string[] = Object.values(PatientListFilterType);

  public patients?: PatientList;
  public pairs: PatientPair[] = [];

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
    this.activeListFilter = patientListFilters[0];
  }

  ngOnInit(): void {
    this.user = this._authService.currentUserValue;

    // init config and patients
    this.loading = true;
    Promise.all([this._initConfiguration(), this._initPatients()]).finally(() => this.loading = false);
  }

  get patientsCount(): number {
    return this.patients ? this.patients.donors.length + this.patients.recipients.length : 0;
  }

  public setActiveFilter(type: string): void {
    this.activeListFilter = patientListFilters.find(f => String(f.type) === type);
  }

  public getFilteredItems(): ListItem[] {
    if (this.activeListFilter && this.patients) {
      if (this.activeListFilter.type === PatientListFilterType.Donors) {
        return this.patients.donors;
      }
      if (this.activeListFilter.type === PatientListFilterType.Recipients) {
        return this.patients.recipients;
      }
    }

    return this.pairs;
  }

  public uploadPatients(): void {
    this._uploadService.uploadFile('Refresh patients', this._initPatients.bind(this));
  }

  private _initPairs(): void {
    if (!this.patients) {
      return;
    }

    // add pairs
    for (const donor of this.patients.donors) {
      const recipient = this.patients.recipients.find(r => r.db_id === donor.related_recipient_db_id);

      if (!recipient) {
        continue;
      }

      this.pairs.push({
        index: this.pairs.length + 1,
        d: donor,
        r: recipient
      });
    }

    // add indexes for list rendering
    this.patients.donors.forEach((d, key) => d.index = key + 1);
    this.patients.recipients.forEach((r, key) => r.index = key + 1);
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

      // Init pairs
      this._initPairs();
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
