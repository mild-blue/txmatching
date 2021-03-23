import { Component, Input, OnInit } from '@angular/core';
import { RecipientEditable } from '@app/model/RecipientEditable';
import { BloodGroup } from '@app/model';
import { NgModel } from '@angular/forms';

@Component({
  selector: 'app-recipient-settings',
  templateUrl: './recipient-settings.component.html',
  styleUrls: ['./recipient-settings.component.scss']
})
export class RecipientSettingsComponent implements OnInit {

  @Input() recipient?: RecipientEditable;
  @Input() showCountryAndMedicalId: boolean = false;
  @Input() showMatchingConditions: boolean = false;
  public allBloodGroups: BloodGroup[] = Object.values(BloodGroup);

  constructor() {
  }

  ngOnInit(): void {
  }

  // HACK: code duplicity with donor-settings.component.ts
  public formatYearOfBirth(inputValue: NgModel) {
    return this.formatNumber(inputValue, 1, new Date().getFullYear());
  }

  // HACK: code duplicity with donor-settings.component.ts
  public formatNumber(inputValue: NgModel, minValue: number = 1, maxValue?: number): void {
    if (!this.recipient) {
      return;
    }

    let newValue: number | undefined;
    if(!inputValue.value) {
      newValue = undefined;
    } else {
      newValue = +inputValue.value;
      if (newValue < minValue) {
        newValue = undefined;
      } else if (maxValue !== undefined && newValue > maxValue) {
        newValue = undefined;
      }
    }

    switch(inputValue.name) {
      case 'antibodiesCutoff': this.recipient.antibodiesCutoff = newValue; break;
      case 'height': this.recipient.height = newValue; break;
      case 'weight': this.recipient.weight = newValue; break;
      case 'yearOfBirth': this.recipient.yearOfBirth = newValue; break;
      case 'previousTransplants': this.recipient.previousTransplants = newValue; break;
      default: throw new Error(`Input with name ${inputValue.name} not implemented.`);
    }

    inputValue.update.emit(newValue);
  }
}
