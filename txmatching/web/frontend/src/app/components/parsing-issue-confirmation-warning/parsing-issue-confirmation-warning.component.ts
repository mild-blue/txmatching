import { Component, Input } from '@angular/core';
import { WarningType } from '@app/helpers/messages';
import { ParsingIssueConfirmation } from '@app/model/ParsingIssueConfirmation';
import { PatientService } from '@app/services/patient/patient.service';
import { LoggerService } from '@app/services/logger/logger.service';
import { AlertService } from '@app/services/alert/alert.service';
import { EventService } from '@app/services/event/event.service';
import { TxmEvent } from '@app/model/Event';

@Component({
  selector: 'parsing-issue-confirmation-warning',
  templateUrl: './parsing-issue-confirmation-warning.component.html',
  styleUrls: ['./parsing-issue-confirmation-warning.component.scss']
})
export class ParsingIssueConfirmationWarningComponent{
  warningType: WarningType = 'warning';
  @Input() data?: ParsingIssueConfirmation;
  @Input() defaultTxmEvent?: TxmEvent;
  public updateSuccess: boolean = false;
  public confirmationLoading: boolean = false;

  constructor(private _patientService: PatientService,
      private _logger: LoggerService,
      private _alertService: AlertService,
      private _eventService: EventService) {
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

    this.confirmationLoading = true;
    this.updateSuccess = false;
    this._patientService.confirmWarning(this.defaultTxmEvent.id, this.data.dbId)
    // .then(res => {
    //   this.data = res;
    // })
    // .catch(() => {
    //   this._logger.error('Error confirming warning');
    // })
    // .finally(() => {
    //   this.confirmationLoading = false;
    // });
  }
}
// todo