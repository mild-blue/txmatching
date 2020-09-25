import { Component, Input, OnInit } from '@angular/core';
import { ListItemDetailComponent } from '@app/components/item-list/item-list.interface';
import { PatientList, PatientPair } from '@app/model/Patient';

@Component({
  selector: 'app-patient-pair-detail',
  templateUrl: './patient-pair-detail.component.html',
  styleUrls: ['./patient-pair-detail.component.scss']
})
export class PatientPairDetailComponent extends ListItemDetailComponent implements OnInit {

  @Input() data?: PatientPair;
  @Input() patients?: PatientList;

  constructor() {
    super();
  }

  ngOnInit(): void {
  }

}
