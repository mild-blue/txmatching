import { Component, Input, OnInit } from '@angular/core';
import { Matching } from '@app/model/Matching';
import { Patient } from '@app/model/Patient';

@Component({
  selector: 'app-matchings-explorer',
  templateUrl: './matchings-explorer.component.html',
  styleUrls: ['./matchings-explorer.component.scss']
})
export class MatchingsExplorerComponent implements OnInit {

  @Input() matchings: Matching[] = [];
  @Input() patients: Patient[] = [];

  public activeMatching?: Matching;

  constructor() {
  }

  ngOnInit(): void {
  }

  public setActive(matching: Matching): void {
    this.activeMatching = matching;
  }

  public getTransplantsCount(matching: Matching): number {
    let sum = 0;
    for (let round of matching.rounds) {
      sum += round.transplants.length;
    }
    return sum;
  }
}
