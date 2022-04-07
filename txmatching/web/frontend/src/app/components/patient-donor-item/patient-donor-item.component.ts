import { Component, Input, OnInit } from '@angular/core';
import { Donor } from '@app/model/Donor';
import { Recipient } from '@app/model';

@Component({
  selector: 'app-patient-donor-item',
  templateUrl: './patient-donor-item.component.html',
  styleUrls: ['./patient-donor-item.component.scss']
})
export class PatientDonorItemComponent implements OnInit{

  @Input() item?: Donor;

  public allMessagesCount: number = 0;
  public mostSevereMessageType: 'errors' | 'warnings' | 'infos' = 'infos';

  constructor() {}

  ngOnInit() {
    this.allMessagesCount = this.countAllMessages(this.item);
    this.mostSevereMessageType = this.findMostSevereMessageType(this.item);
  }

  countAllMessages(data: Donor | Recipient | undefined): number {
    if (!data?.all_messages) {
      return 0;
    }

    return data.all_messages.warnings.length + data.all_messages.errors.length + data.all_messages.infos.length;
  }

  findMostSevereMessageType(donor: Donor | undefined): 'errors' | 'warnings' | 'infos' {
    if (donor?.all_messages.errors.length) {
      return 'errors';
    }

    if (donor?.all_messages.warnings.length) {
      return 'warnings';
    }

    return 'infos';
  }
}
