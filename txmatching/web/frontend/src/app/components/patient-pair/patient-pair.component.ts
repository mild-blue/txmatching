import { Component, Input, OnInit } from '@angular/core';
import { PatientPair } from '@app/model/PatientPair';

@Component({
  selector: 'app-patient-pair',
  templateUrl: './patient-pair.component.html',
  styleUrls: ['./patient-pair.component.scss']
})
export class PatientPairComponent implements OnInit {

  @Input() pair?: PatientPair;

  constructor() {
  }

  ngOnInit(): void {
  }

}
