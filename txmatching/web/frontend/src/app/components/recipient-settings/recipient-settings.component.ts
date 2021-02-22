import { Component, Input, OnInit } from '@angular/core';
import { RecipientEditable } from '@app/model/RecipientEditable';
import { BloodGroup } from '@app/model';

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

}
