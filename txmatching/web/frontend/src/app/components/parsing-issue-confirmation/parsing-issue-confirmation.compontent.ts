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

  sortBy(parsingIssueConfirmation: ParsingIssueConfirmation){
    if (this.warningType === 'warning' && this.data){
      for (let i = 0; i < this.data.length; i++) {
        if (this.data[i].db_id === parsingIssueConfirmation.db_id){
        this.data[i] = parsingIssueConfirmation;
        }
      }
      this.data?.sort((warning) => (warning.confirmed_by === null || warning.confirmed_by === undefined) !! ? -1 : 1);
      console.log(this.data)
    }
  }
}
