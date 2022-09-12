import { Component, Input, OnInit } from "@angular/core";
import { Donor, Recipient } from "@app/model";
import { countAllMessages, patientHasConfirmedWarnings } from "@app/helpers/messages";

@Component({
  selector: "app-warning-overview",
  templateUrl: "./warning-overview.component.html",
  styleUrls: ["./warning-overview.component.scss"],
})
export class WarningOverviewComponent implements OnInit {
  @Input() data: string[] = [];
  @Input() donor?: Donor;
  @Input() recipient?: Recipient;

  public allDonorMessagesCount: number = 0;
  public allRecipientMessagesCount: number = 0;
  public donorHasConfirmedWarnings: boolean = false;
  public recipientHasConfirmedWarnings: boolean = false;

  constructor() {}

  ngOnInit() {
    this.allDonorMessagesCount = countAllMessages(this.donor);
    this.allRecipientMessagesCount = countAllMessages(this.recipient);
    this.donorHasConfirmedWarnings = patientHasConfirmedWarnings(this.donor?.allMessages);
    this.recipientHasConfirmedWarnings = patientHasConfirmedWarnings(this.recipient?.allMessages);
  }
}
