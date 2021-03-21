import { Component, Input } from '@angular/core';
import { Configuration } from '@app/model/Configuration';
import { Matching } from '@app/model/Matching';
import { PatientList } from '@app/model/PatientList';

@Component({
  selector: 'app-matching-item',
  templateUrl: './matching-item.component.html',
  styleUrls: ['./matching-item.component.scss']
})
export class MatchingItemComponent {

  @Input() item?: Matching;
  @Input() isActive: boolean = false;
  @Input() configuration?: Configuration;
  @Input() patients?: PatientList;

  constructor() {
  }

  public getTransplantsCount(matching: Matching): number {
    let sum = 0;
    for (const round of matching.rounds) {
      sum += round.transplants.length;
    }
    return sum;
  }
}
