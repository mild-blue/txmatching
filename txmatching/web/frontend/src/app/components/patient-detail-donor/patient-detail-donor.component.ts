import { Component, OnInit } from '@angular/core';
import { ListItemDetailAbstractComponent } from '@app/components/list-item/list-item.interface';

@Component({
  selector: 'app-patient-detail-donor',
  templateUrl: './patient-detail-donor.component.html',
  styleUrls: ['./patient-detail-donor.component.scss']
})
export class PatientDetailDonorComponent extends ListItemDetailAbstractComponent implements OnInit {

  constructor() {
    super();
  }

  ngOnInit(): void {
  }

}
