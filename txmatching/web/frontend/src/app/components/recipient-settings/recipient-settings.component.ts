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

  public allowPositiveOnly(inputValue: NgModel, minValue: number = 1): void {
    if (!this.recipient) {
      return;
    }

    let newValue: number | undefined;
    if(!inputValue.value) {
      newValue = undefined;
    } else {
      newValue = +inputValue.value;
      newValue = newValue >= minValue ? newValue : undefined;
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
