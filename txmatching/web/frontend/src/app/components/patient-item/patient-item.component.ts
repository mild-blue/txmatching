import { Component, OnInit } from '@angular/core';
import { ListItemAbstractComponent } from '@app/components/list-item/list-item.interface';

@Component({
  selector: 'app-patient-item',
  templateUrl: './patient-item.component.html',
  styleUrls: ['./patient-item.component.scss']
})
export class PatientItemComponent extends ListItemAbstractComponent implements OnInit {

  constructor() {
    super();
  }

  ngOnInit(): void {
  }

}
