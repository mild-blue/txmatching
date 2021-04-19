import { Component, EventEmitter, Input, OnInit, Output } from '@angular/core';
import { AbstractControl, FormBuilder, FormControl, FormGroup, Validators } from '@angular/forms';
import { Configuration } from '@app/model/Configuration';
import { PatientList } from '@app/model/PatientList';
import { HlaCrossmatchLevelGenerated, ScorerGenerated, SolverGenerated } from '@app/generated';

@Component({
  selector: 'app-configuration',
  templateUrl: './configuration.component.html',
  styleUrls: ['./configuration.component.scss']
})
export class ConfigurationComponent implements OnInit {

  @Input() configuration?: Configuration;
  @Input() patients?: PatientList;
  @Output() configSubmitted: EventEmitter<Configuration> = new EventEmitter<Configuration>();

  public configForm?: FormGroup;

  public allScorers: string[] = Object.values(ScorerGenerated);
  public allSolvers: string[] = Object.values(SolverGenerated);

  public allHlaCrossmatchLevels: string[] = Object.values(
    HlaCrossmatchLevelGenerated
  );

  constructor(private _formBuilder: FormBuilder) {
  }

  ngOnInit(): void {
    this._buildFormFromConfig();
  }

  public canSubmit(): boolean {
    return !!this.configForm?.valid;
  }

  public submitAction(): void {
    if (this.configForm && this.configuration) {
      if (!this.canSubmit()) {
        return;
      }
      const { manual_donor_recipient_scores, forbidden_country_combinations, required_patient_db_ids } = this.configuration;

      this.configSubmitted.emit({
        ...this.configForm.value,
        manual_donor_recipient_scores,
        forbidden_country_combinations,
        required_patient_db_ids
      });
    }
  }

  private _buildFormFromConfig(): void {
    if (!this.configuration) {
      return;
    }

    const group: { [key: string]: AbstractControl; } = {};

    const names: string[] = Object.keys(this.configuration);
    for (const name of names) {
      const value = this.configuration[name];
      // check if value is primitive
      if (value !== Object(value)) {
        let validator;
        switch(name) {
          case 'blood_group_compatibility_bonus': validator = Validators.min(0); break;
          case 'minimum_total_score': validator = Validators.min(0); break;
          case 'max_cycle_length': validator = Validators.min(0); break;
          case 'max_sequence_length': validator = Validators.min(0); break;
          case 'max_number_of_distinct_countries_in_round': validator = Validators.min(0); break;
          case 'max_matchings_to_show_to_viewer': validator = Validators.min(0); break;
          case 'max_number_of_matchings': validator = [Validators.min(0), Validators.max(20)]; break;
          case 'max_debt_for_country': validator = Validators.min(0); break;
          case 'max_number_of_dynamic_constrains_ilp_solver': validator = Validators.min(0); break;
          case 'max_debt_for_country_for_blood_group_zero': validator = Validators.min(0); break;
          default: validator = undefined;
        }
        group[name] = new FormControl(value, validator);
      }
    }

    this.configForm = new FormGroup(group);
  }

  public scorerNameToHint(scorerName: string): string {
    switch(scorerName) {
      case ScorerGenerated.SplitScorer:
        return 'The selected scorer SplitScorer computes transplant scores by HLA matches according to their HLA groups using compatibility index. One match in ' +
          'HLA group A increases score by 1, HLA match in group B increases score by 3 and HLA match in group DRB1 increases the ' +
          'score by 9. HLA matches in other groups do not affect the score. Therefore, maximum score for each transplant is ' +
          '1*2 + 3*2 + 9*2 = 26.';
      case ScorerGenerated.HighResScorer:
        return 'The selected scorer HighResScorer computes transplant scores by HLA matches according to their match types. Only matches corresponding ' +
          'to groups A, B and DRB1 increase the score. If the antigens match in HIGH RES representation, the score is ' +
          'increased by 3, if the antigens do not match in HIGH RES representation but they match in SPLIT representation, ' +
          'the score is increased by 2, if the antigens match only in BROAD representation, the score is increased by 1. The maximum ' +
          'score for this scorer is therefore 2*3 + 2*3 + 2*3 = 18.';
      case ScorerGenerated.HighResWithDqdpScorer:
        return 'The selected scorer HighResWithDQDPScorer computes transplant scores by HLA matches according to their match types. Only matches corresponding ' +
          'to groups A, B and DR, DP, DQ and C increase the score. If the antigens match in HIGH RES representation, the score is ' +
          'increased by 3, if the antigens do not match in HIGH RES representation but they match in SPLIT representation, ' +
          'the score is increased by 2, if the antigens match only in BROAD representation, the score is increased by 1. The maximum ' +
          'score for this scorer is therefore 18 (for A, B, DRB1) + 12 (for C, DRB3, DRB4, DRB5) + 24 (for DP, DQ) = 54.';
      default: return 'Please select scorer.';
    }
  }
}
