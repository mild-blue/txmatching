import { Component, Input, OnInit } from '@angular/core';
import { DonorEditable } from '@app/model/DonorEditable';
import { DonorType } from '@app/model';
import { NgModel } from '@angular/forms';
import { formatNumberForPatient, formatYearOfBirthForPatient } from '@app/directives/validators/form.directive';

@Component({
  selector: 'app-donor-settings',
  templateUrl: './donor-settings.component.html',
  styleUrls: ['./donor-settings.component.scss']
})
export class DonorSettingsComponent implements OnInit {

  @Input() donor?: DonorEditable;
  @Input() showCountryMedicalIdAndDonorType: boolean = false;
  @Input() showActiveCheckbox: boolean = false;
  public allDonorTypes: DonorType[] = Object.values(DonorType);

  constructor() {
  }

  ngOnInit(): void {
  }

  public formatYearOfBirth(inputValue: NgModel) {
    if (this.donor) {
      formatYearOfBirthForPatient(inputValue, this.donor);
    }
  }

  public formatNumber(inputValue: NgModel, minValue: number = 1, maxValue?: number): void {
    if (!this.donor) {
      return;
    }

    formatNumberForPatient(inputValue, this.donor, minValue, maxValue);
  }
}
