import { Component, Input, OnInit } from '@angular/core';
import { Donor } from '@app/model/Donor';
import { Recipient } from '@app/model/Recipient';

@Component({
  selector: 'app-patient-pair',
  templateUrl: './patient-pair.component.html',
  styleUrls: ['./patient-pair.component.scss']
})
export class PatientPairComponent implements OnInit {

  @Input() donor?: Donor;
  @Input() recipient?: Recipient;

  constructor() {
  }

  ngOnInit(): void {
  }

}
