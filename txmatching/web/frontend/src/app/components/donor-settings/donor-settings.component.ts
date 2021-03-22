import { Component, Input, OnInit } from '@angular/core';
import { DonorEditable } from '@app/model/DonorEditable';
import { DonorType } from '@app/model';
import { NgModel } from '@angular/forms';

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

  public allowPositiveOnly(inputValue: NgModel): void {
    if (!this.donor) {
      return;
    }

    let newValue: number | undefined;

    if(!inputValue.value) {
      newValue = undefined;
    } else {
      newValue = +inputValue.value;
      newValue = newValue >= 1 ? newValue : undefined;
    }

    switch(inputValue.name) {
      case 'height': this.donor.height = newValue; break;
      case 'weight': this.donor.weight = newValue; break;
      case 'yearOfBirth': this.donor.yearOfBirth = newValue; break;
      default: throw new Error(`Input with name ${inputValue.name} not implemented.`);
    }

    inputValue.update.emit(newValue);
  }
}
