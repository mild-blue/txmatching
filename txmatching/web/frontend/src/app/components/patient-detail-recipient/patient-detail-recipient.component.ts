import { Component, OnInit } from '@angular/core';
import { ListItemDetailAbstractComponent } from '@app/components/list-item/list-item.interface';

@Component({
  selector: 'app-patient-detail-recipient',
  templateUrl: './patient-detail-recipient.component.html',
  styleUrls: ['./patient-detail-recipient.component.scss']
})
export class PatientDetailRecipientComponent extends ListItemDetailAbstractComponent implements OnInit {

  constructor() {
    super();
  }

  ngOnInit(): void {
  }

}
