import { Component, Input, EventEmitter,  OnInit, Output } from '@angular/core';
import { WarningType } from '@app/helpers/messages';
import { ParsingIssueConfirmation } from '@app/model/ParsingIssueConfirmation';
import { PatientService } from '@app/services/patient/patient.service';
import { LoggerService } from '@app/services/logger/logger.service';
import { AlertService } from '@app/services/alert/alert.service';
import { TxmEvent } from '@app/model/Event';
import { getErrorMessage } from '@app/helpers/error';

@Component({
  selector: 'parsing-issue-confirmation-warning',
  templateUrl: './parsing-issue-confirmation-warning.component.html',
  styleUrls: ['./parsing-issue-confirmation-warning.component.scss']
})
export class ParsingIssueConfirmationWarningComponent{
  warningType: WarningType = 'warning';
  @Input() data?: ParsingIssueConfirmation;
  @Input() defaultTxmEvent?: TxmEvent;
  public confirmSuccess: boolean = false;
  public confirmLoading: boolean = false;
  public unconfirmSuccess: boolean = false;
  public unconfirmLoading: boolean = false;

  @Output("sortBy") sortBy: EventEmitter<any> = new EventEmitter();

  constructor(private _patientService: PatientService,
      private _logger: LoggerService,
      private _alertService: AlertService) {
  }

  public confirmAction(): void {
    if (!this.data){
      this._logger.error('confirmAction failed because data not set');
      return;
    }

    if (!this.defaultTxmEvent) {
      this._logger.error('confirmAction failed because defaultTxmEvent not set');
      return;
    }

    this.confirmLoading = true;
    this.confirmSuccess = false;
    this._patientService.confirmWarning(this.defaultTxmEvent.id, this.data.db_id)
    .then(res => {
      if (this.data){
        this.data.confirmed_by = 0;
      }
      this.data = res;
      this.confirmSuccess = true;
      this.sortBy.emit();
    })
    .catch((e) => {
      this._logger.error(`Error confirming warning: "${getErrorMessage(e)}"`);
      this._alertService.error(`Error confirming warning: "${getErrorMessage(e)}"`);
    })
    .finally(() => {
      this.confirmLoading = false;
    });
  }

  public unconfirmAction(): void {
    if (!this.data){
      this._logger.error('unconfirmAction failed because data not set');
      return;
    }

    if (!this.defaultTxmEvent) {
      this._logger.error('unconfirmAction failed because defaultTxmEvent not set');
      return;
    }

    this.unconfirmLoading = true;
    this.unconfirmSuccess = false;
    this._patientService.unconfirmWarning(this.defaultTxmEvent.id, this.data.db_id)
    .then(res => {
      if (this.data){
        this.data.confirmed_by = undefined;
      }
      this.data = res;
      this.unconfirmSuccess = true;
      this.sortBy.emit();
    })
    .catch((e) => {
      this._logger.error(`Error unconfirming warning: "${getErrorMessage(e)}"`);
      this._alertService.error(`Error unconfirming warning: "${getErrorMessage(e)}"`);
    })
    .finally(() => {
      this.unconfirmLoading = false;
    });
  }
}
