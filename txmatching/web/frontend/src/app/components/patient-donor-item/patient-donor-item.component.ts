import { Component, Input, OnInit } from '@angular/core';
import { Donor } from '@app/model/Donor';

@Component({
  selector: 'app-patient-donor-item',
  templateUrl: './patient-donor-item.component.html',
  styleUrls: ['./patient-donor-item.component.scss']
})
export class PatientDonorItemComponent implements OnInit {

  @Input() item?: Donor;

  constructor() {
  }

  ngOnInit(): void {
  }
}
