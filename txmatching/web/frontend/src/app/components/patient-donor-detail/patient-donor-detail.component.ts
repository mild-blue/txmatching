import { Component, Input, OnInit } from '@angular/core';
import { ListItemDetailAbstractComponent } from '@app/components/list-item/list-item.interface';
import { PatientService } from '@app/services/patient/patient.service';
import { Donor } from '@app/model/Donor';
import { PatientList } from '@app/model/PatientList';
import { TxmEvent } from '@app/model/Event';
import { LoggerService } from '@app/services/logger/logger.service';
import { DonorEditable } from '@app/model/DonorEditable';
import { AlertService } from '@app/services/alert/alert.service';
import { faTrash } from '@fortawesome/free-solid-svg-icons';
import { EventService } from '@app/services/event/event.service';
import { getErrorMessage } from '@app/helpers/error';

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
  public deleteLoading: boolean = false;
  public deleteSuccess: boolean = false;
  public deleteIcon = faTrash;

  constructor(private _patientService: PatientService,
              private _logger: LoggerService,
              private _alertService: AlertService,
              private _eventService: EventService) {
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
    this._patientService.saveDonor(
      this.defaultTxmEvent.id, this.item.dbId,
      this.donorEditable, this._eventService.getConfigId()
    )
    .then((updatedDonor) => {
      this._logger.log('Updated donor received from BE', [updatedDonor]);

      if (this.item) {
        updatedDonor.donor.index = this.item.index;
        Object.assign(this.item, updatedDonor.donor);
      }

      if (updatedDonor.parsingErrors.length > 0) {
        this._alertService.infoWithParsingErrors(
          'Donor was updated but some parsing errors and warnings occurred. ' +
          'You can modify the patient to fix the issues or contact us if the issues are not clear on info@mild.blue or +420 723 927 536.',
          updatedDonor.parsingErrors
        );
        this._logger.log('Parsing errors', updatedDonor.parsingErrors);
      }

      this._initDonorEditable();
      this.success = true;
    })
    .catch((e) => {
      this._alertService.error(`Error saving donor: "${getErrorMessage(e)}"`);
      this._logger.error(`Error saving donor: "${getErrorMessage(e)}"`);
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

  public handleDeleteDonor(): void {
    if (!this.item) {
      this._logger.error('handleDeleteDonor failed because item not set');
      return;
    }
    if (!this.defaultTxmEvent) {
      this._logger.error('handleDeleteDonor failed because defaultTxmEvent not set');
      return;
    }

    const message = this.item.relatedRecipientDbId != undefined
      ? 'Are you sure you want to remove donor and its recipient?'
      : 'Are you sure you want to remove donor?';
    if (!confirm(message)) {
      return;
    }

    this.deleteLoading = true;
    this.deleteSuccess = false;
    this._patientService.deleteDonor(this.defaultTxmEvent.id, this.item.dbId)
    .then(() => {
      this.deleteSuccess = true;
    })
    .catch(() => {
      this._logger.error('Error deleting donor');
    })
    .finally(() => {
      this.deleteLoading = false;
    });
  }
}
