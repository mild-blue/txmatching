import { Component, Input, OnInit } from '@angular/core';
import { Donor, DonorType } from '@app/model/Donor';

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

  public getDonorTypeLabel(type: DonorType): string {
    if (type === DonorType.BRIDGING_DONOR) {
      return 'bridging donor';
    } else if (type === DonorType.NON_DIRECTED) {
      return 'non-directed donor';
    }

    return '';
  }
}
