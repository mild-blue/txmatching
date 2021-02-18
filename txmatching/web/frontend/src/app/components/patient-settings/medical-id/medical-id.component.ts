import { Component, Input, OnInit } from '@angular/core';
import { PatientEditable } from '@app/model/PatientEditable';

@Component({
  selector: 'app-medical-id',
  templateUrl: './medical-id.component.html',
  styleUrls: ['./medical-id.component.scss']
})
export class MedicalIdComponent implements OnInit {

  @Input() patient?: PatientEditable;

  constructor() {
  }

  ngOnInit(): void {
  }

}
