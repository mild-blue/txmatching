import { Component, Input, OnInit } from '@angular/core';
import { ListItemAbstractComponent } from '@app/components/list-item/list-item.interface';
import { PatientPair } from '@app/model/PatientPair';
import { countAllMessages, findMostSevereMessageType, patientHasConfirmedWarnings, WarningType } from '@app/helpers/messages';

@Component({
  selector: 'app-patient-pair-item',
  templateUrl: './patient-pair-item.component.html',
  styleUrls: ['./patient-pair-item.component.scss']
})
export class PatientPairItemComponent extends ListItemAbstractComponent implements OnInit {

  @Input() item?: PatientPair;

  public allMessagesCount: number = 0;
  public mostSevereMessageType: WarningType = 'info';
  public allWarningsConfirmed?: boolean;

  constructor() {
    super();
  }

  ngOnInit() {
    this.allMessagesCount = countAllMessages(this.item?.d) + countAllMessages(this.item?.r);
    this.mostSevereMessageType = findMostSevereMessageType(this.item?.d, this.item?.r);
    this.allWarningsConfirmed = patientHasConfirmedWarnings(this.item?.d?.allMessages) &&
                                patientHasConfirmedWarnings(this.item?.r?.allMessages);
  }
}

      