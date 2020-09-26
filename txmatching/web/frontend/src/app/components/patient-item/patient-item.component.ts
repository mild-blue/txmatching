import { Component, Input, OnInit } from '@angular/core';
import { ListItemAbstractComponent } from '@app/components/list-item/list-item.interface';
import { Patient } from '@app/model/Patient';

@Component({
  selector: 'app-patient-item',
  templateUrl: './patient-item.component.html',
  styleUrls: ['./patient-item.component.scss']
})
export class PatientItemComponent extends ListItemAbstractComponent implements OnInit {

  @Input() item?: Patient;

  constructor() {
    super();
  }

  ngOnInit(): void {
  }

}
