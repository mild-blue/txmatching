import { Component, Input, OnInit } from '@angular/core';
import { ListItemAbstractComponent } from '@app/components/list-item/list-item.interface';
import { PatientPair } from '@app/model/Patient';

@Component({
  selector: 'app-patient-pair-item',
  templateUrl: './patient-pair-item.component.html',
  styleUrls: ['./patient-pair-item.component.scss']
})
export class PatientPairItemComponent extends ListItemAbstractComponent implements OnInit {

  @Input() item?: PatientPair;

  constructor() {
    super();
  }

  ngOnInit(): void {
  }

}
