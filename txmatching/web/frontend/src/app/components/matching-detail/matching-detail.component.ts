import { Component, Input } from '@angular/core';
import { PatientList } from '@app/model/Patient';
import { ListItemDetailAbstractComponent } from '@app/components/list-item/list-item.interface';
import { Matching } from '@app/model/Matching';

@Component({
  selector: 'app-matching-detail',
  templateUrl: './matching-detail.component.html',
  styleUrls: ['./matching-detail.component.scss']
})
export class MatchingDetailComponent extends ListItemDetailAbstractComponent {

  @Input() item?: Matching;
  @Input() patients?: PatientList;

  constructor() {
    super();
  }
}
