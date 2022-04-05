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
    if (!data) {
      return 0;
    }

    return data.all_messages.warnings.length + data.all_messages.infos.length + data.all_messages.errors.length;
  }
}
