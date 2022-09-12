import { Component, Input, OnInit } from "@angular/core";
import { Configuration } from "@app/model/Configuration";

@Component({
  selector: "app-score-indicator",
  templateUrl: "./score-indicator.component.html",
  styleUrls: ["./score-indicator.component.scss"],
})
export class ScoreIndicatorComponent implements OnInit {
  @Input() score?: number;
  @Input() maxScore?: number;
  @Input() showScore?: boolean;

  constructor() {}

  ngOnInit(): void {}

  public percentage(score: number | undefined, maxScore: number | undefined): number {
    if (!score) {
      return 0;
    }

    return (100 * (score ?? 0)) / (maxScore ?? 1);
  }
}
