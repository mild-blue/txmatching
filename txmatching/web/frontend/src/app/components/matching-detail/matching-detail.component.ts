import { Component, Input } from '@angular/core';
import { MatchingView } from '@app/model/Matching';
import { PatientList } from '@app/model/Patient';
import { ListItemDetailAbstractComponent } from '@app/components/list-item/list-item.interface';

@Component({
  selector: 'app-matching-detail',
  templateUrl: './matching-detail.component.html',
  styleUrls: ['./matching-detail.component.scss']
})
export class MatchingDetailComponent extends ListItemDetailAbstractComponent {

  @Input() item?: MatchingView;
  @Input() patients?: PatientList;

  constructor() {
    super();
  }
}
