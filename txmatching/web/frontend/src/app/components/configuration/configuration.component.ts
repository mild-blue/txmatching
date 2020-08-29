import { Component, Input, OnInit } from '@angular/core';
import { AbstractControl, FormBuilder, FormControl, FormGroup } from '@angular/forms';
import { Configuration } from '@app/model/Configuration';

@Component({
  selector: 'app-configuration',
  templateUrl: './configuration.component.html',
  styleUrls: ['./configuration.component.scss']
})
export class ConfigurationComponent implements OnInit {

  @Input() configuration?: Configuration;

  public configForm: FormGroup;

  constructor(private _formBuilder: FormBuilder) {
    this.configForm = new FormGroup({
      firstBox: new FormGroup({
        enforce_compatible_blood_group: new FormControl(false),
        require_new_donor_having_better_match_in_compatibility_index: new FormControl(false),
        require_new_donor_having_better_match_in_compatibility_index_or_blood_group: new FormControl(false),
        use_binary_scoring: new FormControl(false)
      }),
      secondBox: new FormGroup({
        minimum_total_score: new FormControl(''),
        max_cycle_length: new FormControl(''),
        max_sequence_length: new FormControl(''),
        max_number_of_distinct_countries_in_round: new FormControl('')
      }),
      thirdBox: new FormGroup({
        manual_donor_recipient_scores_dtoe: new FormControl('')
      })
    });
  }

  get firstBox(): FormGroup {
    return this.configForm.get('firstBox') as FormGroup;
  }

  get formBoxes(): { [key: string]: AbstractControl; } {
    return this.configForm.controls;
  }

  ngOnInit(): void {
    console.log('oninit');
    this._buildFormFromConfig();
  }

  private _buildFormFromConfig(): void {
    if (!this.configuration) {
      return;
    }

    const group: { [key: string]: AbstractControl; } = {};

    console.log(this.configuration);
    const names: string[] = Object.keys(this.configuration);
    for (let name of names) {
      const value = this.configuration[name];
      group[name] = new FormControl(value);
    }

    this.configForm = new FormGroup(group);
  }
}
