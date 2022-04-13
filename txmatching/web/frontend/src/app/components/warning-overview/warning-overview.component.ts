import { Component, Input, OnInit } from '@angular/core';
import { Donor, Recipient } from '@app/model';
import { countAllMessages } from '@app/helpers/messages';

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
    this.allDonorMessagesCount = countAllMessages(this.donor);
    this.allRecipientMessagesCount = countAllMessages(this.recipient);
  }
}
