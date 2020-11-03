import { Component, Input, OnInit } from '@angular/core';
import { Configuration } from '@app/model/Configuration';

@Component({
  selector: 'app-score-indicator',
  templateUrl: './score-indicator.component.html',
  styleUrls: ['./score-indicator.component.scss']
})
export class ScoreIndicatorComponent implements OnInit {

  @Input() configuration?: Configuration;
  @Input() score?: number;

  constructor() {
  }

  ngOnInit(): void {
  }

  public percentage(score: number | undefined): number {
    if (!this.configuration || !score) {
      return 0;
    }

    const maxScore = this.configuration.maximum_total_score;
    return 100 * (score ?? 0) / maxScore;
  }
}
