import { Component, Input, EventEmitter, Output } from '@angular/core';
import { WarningType } from '@app/helpers/messages';
import { ParsingIssueConfirmation } from '@app/model/ParsingIssueConfirmation';
import { PatientService } from '@app/services/patient/patient.service';
import { LoggerService } from '@app/services/logger/logger.service';
import { AlertService } from '@app/services/alert/alert.service';
import { TxmEvent } from '@app/model/Event';
import { getErrorMessage } from '@app/helpers/error';

@Component({
  selector: 'app-parsing-issue-confirmation-warning',
  templateUrl: './parsing-issue-confirmation-warning.component.html',
  styleUrls: ['./parsing-issue-confirmation-warning.component.scss']
})
export class ParsingIssueConfirmationWarningComponent {
  warningType: WarningType = 'warning';
  @Input() data?: ParsingIssueConfirmation;
  @Input() defaultTxmEvent?: TxmEvent;
  public success: boolean = false;
  public loading: boolean = false;

  @Output() sortBy: EventEmitter<ParsingIssueConfirmation> = new EventEmitter();

  constructor(private _patientService: PatientService,
              private _logger: LoggerService,
              private _alertService: AlertService) {
  }

  public confirmAction(confirm: boolean): void {
    if (!this.data) {
      this._logger.error('confirmAction failed because data not set');
      return;
    }

    if (!this.defaultTxmEvent) {
      this._logger.error('confirmAction failed because defaultTxmEvent not set');
      return;
    }

    const confirmationService = (confirm) ?
      this._patientService.confirmWarning(this.defaultTxmEvent.id, this.data.dbId) :
      this._patientService.unconfirmWarning(this.defaultTxmEvent.id, this.data.dbId);

    this.loading = true;

    confirmationService.then(res => {
      this.data = res;
      this.sortBy.emit(this.data);
      this.success = true;
    })
    .catch((e) => {
      this._logger.error(`Error confirming warning: "${getErrorMessage(e)}"`);
      this._alertService.error(`Error confirming warning: "${getErrorMessage(e)}"`);
      this.success = false;
    })
    .finally(() => this.loading = false);
  }
}
