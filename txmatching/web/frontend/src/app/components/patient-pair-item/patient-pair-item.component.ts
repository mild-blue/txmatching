import { Component, Input, OnInit } from '@angular/core';
import { ListItemComponent } from '@app/components/item-list/item-list.interface';
import { AppConfiguration } from '@app/model/Configuration';
import { PatientList, PatientPair } from '@app/model/Patient';

@Component({
  selector: 'app-patient-pair-item',
  templateUrl: './patient-pair-item.component.html',
  styleUrls: ['./patient-pair-item.component.scss']
})
export class PatientPairItemComponent extends ListItemComponent implements OnInit {

  @Input() data?: PatientPair;
  @Input() isActive: boolean = false;
  @Input() configuration?: AppConfiguration;
  @Input() patients?: PatientList;

  constructor() {
    super();
  }

  ngOnInit(): void {
  }

}
