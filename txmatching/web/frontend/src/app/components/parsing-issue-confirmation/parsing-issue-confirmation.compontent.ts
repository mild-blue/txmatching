import { Component, Input } from "@angular/core";
import { WarningType } from "@app/helpers/messages";
import { ParsingIssueConfirmation } from "@app/model/ParsingIssueConfirmation";
import { TxmEvent } from "@app/model/Event";

@Component({
  selector: "app-parsing-issue-confirmation",
  templateUrl: "./parsing-issue-confirmation.component.html",
  styleUrls: ["./parsing-issue-confirmation.component.scss"],
})
export class ParsingIssueConfirmationComponent {
  @Input() warningType: WarningType = "info";
  @Input() data?: ParsingIssueConfirmation[];
  @Input() defaultTxmEvent?: TxmEvent;

  constructor() {}

  sortBy(parsingIssueConfirmation: ParsingIssueConfirmation) {
    if (this.warningType === "warning" && this.data) {
      const index: number = this.data.map((parsingIssue) => parsingIssue.dbId).indexOf(parsingIssueConfirmation.dbId);
      if (index !== -1) {
        this.data[index] = parsingIssueConfirmation;
      }
      this.data?.sort((warning) => (!warning.confirmedBy ? -1 : 1));
    }
  }
}
