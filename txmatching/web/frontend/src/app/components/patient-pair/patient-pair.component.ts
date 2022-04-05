import { Component, Input } from '@angular/core';
import { Donor } from '@app/model/Donor';
import { Recipient } from '@app/model/Recipient';
import { PatientPairStyle } from '@app/components/patient-pair/patient-pair.interface';

@Component({
  selector: 'app-patient-pair',
  templateUrl: './patient-pair.component.html',
  styleUrls: ['./patient-pair.component.scss']
})
export class PatientPairComponent {

  @Input() donor?: Donor;
  @Input() recipient?: Recipient;
  @Input() showWarning: boolean = false;
  @Input() style: PatientPairStyle = PatientPairStyle.Default;

  constructor() {
  }
}
