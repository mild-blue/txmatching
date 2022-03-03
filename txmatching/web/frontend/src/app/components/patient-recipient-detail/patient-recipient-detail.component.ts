import {Component, Input, OnInit} from '@angular/core';
import {ListItemDetailAbstractComponent} from '@app/components/list-item/list-item.interface';
import {PatientService} from '@app/services/patient/patient.service';
import {Recipient} from '@app/model/Recipient';
import {PatientList} from '@app/model/PatientList';
import {TxmEvent} from '@app/model/Event';
import {RecipientEditable} from '@app/model/RecipientEditable';
import {LoggerService} from '@app/services/logger/logger.service';
import {AlertService} from '@app/services/alert/alert.service';
import {getErrorMessage} from "@app/helpers/error";

@Component({
  selector: 'app-patient-detail-recipient',
  templateUrl: './patient-recipient-detail.component.html',
  styleUrls: ['./patient-recipient-detail.component.scss']
})
export class PatientRecipientDetailComponent extends ListItemDetailAbstractComponent implements OnInit {

  @Input() patients?: PatientList;
  @Input() item?: Recipient;
  @Input() defaultTxmEvent?: TxmEvent;

  public recipientEditable?: RecipientEditable;

  public loading: boolean = false;
  public success: boolean = false;

  constructor(private _patientService: PatientService,
              private _logger: LoggerService,
              private _alertService: AlertService) {
    super(_patientService);
  }

  ngOnInit(): void {
    this._initRecipientEditable();
  }

  public handleSave(): void {
    if (!this.item) {
      return;
    }
    if (!this.recipientEditable) {
      return;
    }
    if (!this.defaultTxmEvent) {
      return;
    }

    this.loading = true;
    this.success = false;
    this._patientService.saveRecipient(this.defaultTxmEvent.id, this.item.dbId, this.recipientEditable)
    .then((updatedRecipient) => {
      this._logger.log('Updated recipient received from BE', [updatedRecipient]);
      Object.assign(this.item, updatedRecipient.recipient);

      if (updatedRecipient.parsingErrors.length > 0) {
        this._alertService.infoWithParsingErrors(
          'Recipient was updated but some parsing errors and warnings occurred. ' +
          'You can modify the patient to fix the issues or contact us if the issues are not clear on info@mild.blue or +420 723 927 536.',
          updatedRecipient.parsingErrors
        );
        this._logger.log('Parsing errors', updatedRecipient.parsingErrors);
      }

      this._initRecipientEditable();
      this.success = true;
    })
    .catch((e) => {
      this._alertService.error(`Error saving recipient: "${getErrorMessage(e)}"`);
      this._logger.error(`Error saving recipient: "${getErrorMessage(e)}"`);
    })
    .finally(() => this.loading = false);
  }

  private _initRecipientEditable() {
    if (!this.item) {
      this._logger.error('_initDonorEditable failed because item not set');
      return;
    }

    this.recipientEditable = new RecipientEditable();
    this.recipientEditable.initializeFromPatient(this.item);
    this._logger.log('RecipientEditable initialized', [this.recipientEditable]);
  }
}
