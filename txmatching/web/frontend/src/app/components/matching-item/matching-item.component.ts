import { Component, Input } from '@angular/core';
import { AppConfiguration } from '@app/model/Configuration';
import { ListItemAbstractComponent } from '@app/components/list-item/list-item.interface';
import { Matching } from '@app/model/Matching';
import { PatientList } from '@app/model/PatientList';

@Component({
  selector: 'app-matching-item',
  templateUrl: './matching-item.component.html',
  styleUrls: ['./matching-item.component.scss']
})
export class MatchingItemComponent extends ListItemAbstractComponent {

  @Input() item?: Matching;
  @Input() isActive: boolean = false;
  @Input() configuration?: AppConfiguration;
  @Input() patients?: PatientList;

  constructor() {
    super();
  }

  public getTransplantsCount(matching: Matching): number {
    let sum = 0;
    for (const round of matching.rounds) {
      sum += round.transplants.length;
    }
    return sum;
  }
}
