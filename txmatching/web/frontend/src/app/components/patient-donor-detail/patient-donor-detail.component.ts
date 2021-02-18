import { Component, Input, OnInit } from '@angular/core';
import { ListItemDetailAbstractComponent } from '@app/components/list-item/list-item.interface';
import { PatientService } from '@app/services/patient/patient.service';
import { Donor } from '@app/model/Donor';
import { PatientList } from '@app/model/PatientList';
import { TxmEvent } from '@app/model/Event';
import { LoggerService } from '@app/services/logger/logger.service';
import { DonorEditable } from '@app/model/DonorEditable';
import { AlertService } from '@app/services/alert/alert.service';

@Component({
  selector: 'app-patient-detail-donor',
  templateUrl: './patient-donor-detail.component.html',
  styleUrls: ['./patient-donor-detail.component.scss']
})
export class PatientDonorDetailComponent extends ListItemDetailAbstractComponent implements OnInit {

  @Input() patients?: PatientList;
  @Input() item?: Donor;
  @Input() defaultTxmEvent?: TxmEvent;

  public donorEditable?: DonorEditable;

  public loading: boolean = false;
  public success: boolean = false;

  constructor(private _patientService: PatientService,
              private _logger: LoggerService,
              private _alertService: AlertService) {
    super(_patientService);
  }

  ngOnInit(): void {
    this._initDonorEditable();
  }

  public handleSave(): void {
    if (!this.item) {
      this._logger.error('handleSave failed because item not set');
      return;
    }
    if (!this.donorEditable) {
      this._logger.error('handleSave failed because donorEditable not set');
      return;
    }
    if (!this.defaultTxmEvent) {
      this._logger.error('handleSave failed because defaultTxmEvent not set');
      return;
    }

    this.loading = true;
    this.success = false;
    this._patientService.saveDonor(this.defaultTxmEvent.id, this.item.db_id, this.donorEditable)
    .then((updatedDonor) => {
      this._logger.log('Updated donor received from BE', [updatedDonor]);
      Object.assign(this.item, updatedDonor);
      this._initDonorEditable();
      this.success = true;
    })
    .catch((e) => {
      // TODOO: better alert reporting?
      this._alertService.error(`Error saving donor: "${e.message || e}"`);
      this._logger.error(`Error saving donor: "${e.message || e}"`);
    })
    .finally(() => this.loading = false);
  }

  private _initDonorEditable() {
    if (!this.item) {
      this._logger.error('_initDonorEditable failed because item not set');
      return;
    }

    this.donorEditable = new DonorEditable();
    this.donorEditable.initializeFromPatient(this.item);
    this._logger.log('DonorEditable initialized', [this.donorEditable]);
  }
}
