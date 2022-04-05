import { Component, Input, OnInit } from '@angular/core';
import { ListItemAbstractComponent } from '@app/components/list-item/list-item.interface';
import { PatientPair } from '@app/model/PatientPair';
import { Donor, Recipient } from '@app/model';

@Component({
  selector: 'app-patient-pair-item',
  templateUrl: './patient-pair-item.component.html',
  styleUrls: ['./patient-pair-item.component.scss']
})
export class PatientPairItemComponent extends ListItemAbstractComponent implements OnInit {

  @Input() item?: PatientPair;

  public allMessagesCount: number = 0;
  public mostSevereMessageType: 'errors' | 'warnings' | 'infos' = 'infos';

  constructor() {
    super();
  }

  ngOnInit() {
    this.allMessagesCount = this.countAllMessages(this.item?.d) + this.countAllMessages(this.item?.r);
    this.mostSevereMessageType = this.findMostSevereMessageType(this.item?.d, this.item?.r);
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

  findMostSevereMessageType(donor: Donor | undefined, recipient: Recipient | undefined): 'errors' | 'warnings' | 'infos' {
    if (!donor?.all_messages?.errors || !donor?.all_messages?.warnings ||
      !recipient?.all_messages?.errors || !recipient?.all_messages?.warnings) {
      return 'infos';
    }

    if (donor?.all_messages.errors.length || recipient?.all_messages.errors.length) {
      return 'errors';
    }
    if (donor?.all_messages.warnings.length || recipient?.all_messages.warnings.length) {
      return 'warnings';
    }
    return 'infos';
  }
}
