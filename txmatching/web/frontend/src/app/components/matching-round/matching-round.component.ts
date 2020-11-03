import { Component, Input } from '@angular/core';
import { Round } from '@app/model/Matching';
import { PatientList } from '@app/model/Patient';
import { faAngleRight } from '@fortawesome/free-solid-svg-icons';
import { AppConfiguration } from '@app/model/Configuration';
import { UiInteractionsService } from '@app/services/ui-interactions/ui-interactions.service';

@Component({
  selector: 'app-matching-round',
  templateUrl: './matching-round.component.html',
  styleUrls: ['./matching-round.component.scss']
})
export class MatchingRoundComponent {

  @Input() round?: Round;
  @Input() patients?: PatientList;
  @Input() configuration?: AppConfiguration;

  public arrowRight = faAngleRight;

  constructor(private _uiInteractionsService: UiInteractionsService) {
  }

  public setActiveTransplant(id: number): void {
    this._uiInteractionsService.setFocusedTransplantId(id);
  }
}
