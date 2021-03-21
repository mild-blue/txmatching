import { Component, Input } from '@angular/core';
import { faAngleRight } from '@fortawesome/free-solid-svg-icons';
import { Configuration } from '@app/model/Configuration';
import { UiInteractionsService } from '@app/services/ui-interactions/ui-interactions.service';
import { Round } from '@app/model/Round';

@Component({
  selector: 'app-matching-round',
  templateUrl: './matching-round.component.html',
  styleUrls: ['./matching-round.component.scss']
})
export class MatchingRoundComponent {

  @Input() round?: Round;
  @Input() configuration?: Configuration;

  public arrowRight = faAngleRight;

  constructor(private _uiInteractionsService: UiInteractionsService) {
  }

  public setActiveTransplant(id: number): void {
    this._uiInteractionsService.setFocusedTransplantId(id);
  }
}
