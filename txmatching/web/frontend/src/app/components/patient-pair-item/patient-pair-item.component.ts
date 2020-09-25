import { Component, Input, OnInit } from '@angular/core';
import { ListItemAbstractComponent } from '@app/components/list-item/list-item.interface';
import { AppConfiguration } from '@app/model/Configuration';
import { PatientList, PatientPair } from '@app/model/Patient';

@Component({
  selector: 'app-patient-pair-item',
  templateUrl: './patient-pair-item.component.html',
  styleUrls: ['./patient-pair-item.component.scss']
})
export class PatientPairItemComponent extends ListItemAbstractComponent implements OnInit {

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
