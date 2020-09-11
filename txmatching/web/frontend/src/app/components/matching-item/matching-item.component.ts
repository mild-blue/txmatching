import { Component, Input, OnInit } from '@angular/core';
import { MatchingView } from '@app/model/Matching';
import { PatientList } from '@app/model/Patient';
import { AppConfiguration } from '@app/model/Configuration';

@Component({
  selector: 'app-matching-item',
  templateUrl: './matching-item.component.html',
  styleUrls: ['./matching-item.component.scss']
})
export class MatchingItemComponent implements OnInit {

  @Input() matching?: MatchingView;
  @Input() isActive: boolean = false;
  @Input() configuration?: AppConfiguration;
  @Input() patients?: PatientList;

  constructor() {
  }

  ngOnInit(): void {
  }

  public getTransplantsCount(matching: MatchingView): number {
    let sum = 0;
    for (const round of matching.rounds) {
      sum += round.transplants.length;
    }
    return sum;
  }
}
