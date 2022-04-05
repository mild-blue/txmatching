import { Component, Input, OnInit } from '@angular/core';
import { Donor, Recipient } from '@app/model';

@Component({
  selector: 'app-warning-overview',
  templateUrl: './warning-overview.component.html',
  styleUrls: ['./warning-overview.component.scss']
})
export class WarningOverviewComponent implements OnInit{

  @Input() data: string[] = [];
  @Input() donor?: Donor;
  @Input() recipient?: Recipient;

  public allDonorMessagesCount: number = 0;
  public allRecipientMessagesCount: number = 0;

  constructor() {}

  ngOnInit() {
    this.allDonorMessagesCount = this.countAllMessages(this.donor);
    this.allRecipientMessagesCount = this.countAllMessages(this.recipient);
  }

  countAllMessages(data: Donor | Recipient | undefined): number {
    let sumOfMessages = 0;

    if (data?.all_messages?.warnings) {
      sumOfMessages += data.all_messages.warnings.length;
    }

    if (data?.all_messages?.errors) {
      sumOfMessages += data.all_messages.errors.length;
    }

    if (data?.all_messages?.infos) {
      sumOfMessages += data.all_messages.infos.length;
    }

    return sumOfMessages;
  }
}
