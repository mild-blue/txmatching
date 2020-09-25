import { Component, Input, OnInit } from '@angular/core';
import { MatchingView } from '@app/model/Matching';
import { PatientList } from '@app/model/Patient';
import { AppConfiguration } from '@app/model/Configuration';
import { ListItemComponent } from '@app/components/item-list/item-list.interface';

@Component({
  selector: 'app-matching-item',
  templateUrl: './matching-item.component.html',
  styleUrls: ['./matching-item.component.scss']
})
export class MatchingItemComponent extends ListItemComponent implements OnInit {

  @Input() data?: MatchingView;
  @Input() isActive: boolean = false;
  @Input() configuration?: AppConfiguration;
  @Input() patients?: PatientList;

  constructor() {
    super();
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
