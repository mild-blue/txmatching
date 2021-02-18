import { Component, Input, OnInit } from '@angular/core';
import { PatientEditable } from '@app/model/PatientEditable';
import { BloodGroup } from '@app/model';

@Component({
  selector: 'app-blood-group',
  templateUrl: './blood-group.component.html',
  styleUrls: ['./blood-group.component.scss']
})
export class BloodGroupComponent implements OnInit {

  @Input() patient?: PatientEditable;
  public allBloodGroups: BloodGroup[] = Object.values(BloodGroup);

  constructor() {
  }

  ngOnInit(): void {
  }

}
