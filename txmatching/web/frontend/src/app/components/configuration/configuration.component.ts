import { Component, EventEmitter, Input, OnInit, Output } from '@angular/core';
import { AbstractControl, FormBuilder, FormControl, FormGroup } from '@angular/forms';
import { Configuration } from '@app/model/Configuration';
import { PatientList } from '@app/model/PatientList';
import { ScorerGenerated, SolverGenerated, HlaCrossmatchLevelGenerated } from '@app/generated';

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

  public submitAction(): void {
    if (this.configForm && this.configuration) {
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
        group[name] = new FormControl(value);
      }
    }

    this.configForm = new FormGroup(group);
  }

  public scorerNameToHint(scorerName: string): string {
    switch(scorerName) {
      case ScorerGenerated.SplitHlaAdditiveScorer:
        return 'The selected scorer SplitHlaAdditiveScorer computes transplant scores by HLA matches according to their HLA groups. One match in ' +
          'HLA group A increases score by 9, HLA match in group B increases score by 3 and HLA match in group DRB1 increases the ' +
          'score by 1. HLA matches in other groups does not affect the score. Therefore, maximum score for each transplant is ' +
          '9*2 + 3*2 + 2*1 = 26.';
      case ScorerGenerated.HighResHlaAdditiveScorer:
        return 'The selected scorer HighResHlaAdditiveScorer computes transplant scores by HLA matches according to their match types. Only matches corresponding ' +
          'to groups A, B and DRB1 increase the score. If the antigens match through HIGH RES representation, the score is ' +
          'increased by 3, if the antigens do not match through HIGH RES representation but they match through SPLIT representation, ' +
          'the score is increased by 2, if the antigens match only through BROAD representation, the score is increased by 1. The maximum ' +
          'score for this scorer is therefore 2*3 + 2*2 + 2*1 = 12.';
      default: return 'Please select scorer.';
    }
  }
}
