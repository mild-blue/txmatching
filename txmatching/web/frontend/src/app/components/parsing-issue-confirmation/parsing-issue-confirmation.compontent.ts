import { Component, Input } from '@angular/core';
import { WarningType } from '@app/helpers/messages';
import { ParsingIssueConfirmation } from '@app/model/ParsingIssueConfirmation';
import { TxmEvent } from '@app/model/Event';

@Component({
  selector: 'parsing-issue-confirmation',
  templateUrl: './parsing-issue-confirmation.component.html',
  styleUrls: ['./parsing-issue-confirmation.component.scss']
})
export class ParsingIssueConfirmationComponent{
  @Input() warningType: WarningType = 'info';
  @Input() data?: Array<ParsingIssueConfirmation>;
  @Input() defaultTxmEvent?: TxmEvent;

  constructor() { }
}
