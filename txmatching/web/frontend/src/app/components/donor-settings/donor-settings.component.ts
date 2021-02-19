import { Component, Input, OnInit } from '@angular/core';
import { DonorEditable } from '@app/model/DonorEditable';
import { DonorType } from '@app/model';

@Component({
  selector: 'app-donor-settings',
  templateUrl: './donor-settings.component.html',
  styleUrls: ['./donor-settings.component.scss']
})
export class DonorSettingsComponent implements OnInit {

  @Input() donor?: DonorEditable;
  public allDonorTypes: DonorType[] = Object.values(DonorType);

  constructor() {
  }

  ngOnInit(): void {
  }

}
