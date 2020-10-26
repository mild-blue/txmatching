import { Component, Input } from '@angular/core';
import { faAngleRight } from '@fortawesome/free-solid-svg-icons';
import { AppConfiguration } from '@app/model/Configuration';
import { Round } from '@app/model/Round';
import { Transplant } from '@app/model/Transplant';
import { DonorType } from '@app/model/Donor';
import { PatientList } from '@app/model/PatientList';

@Component({
  selector: 'app-matching-round',
  templateUrl: './matching-round.component.html',
  styleUrls: ['./matching-round.component.scss']
})
export class MatchingRoundComponent {

  @Input() round?: Round;
  @Input() index: number = 0;
  @Input() patients?: PatientList;
  @Input() configuration?: AppConfiguration;

  public arrowRight = faAngleRight;

  get roundIndex(): string {
    const roundIndex = `${this.index}`;
    if (!this.round?.transplants.length) {
      return roundIndex;
    }

    const firstTransplant = this.round.transplants[0];
    const donor = firstTransplant.d;

    if (donor) {
      if (donor.donor_type === DonorType.BRIDGING_DONOR.valueOf()) {
        return `${roundIndex}B`;
      }
      if (donor.donor_type === DonorType.NON_DIRECTED.valueOf()) {
        return `${roundIndex}N`;
      }
    }

    return roundIndex;
  }

  public percentageScore(transplant: Transplant): number {
    if (!this.configuration) {
      return 0;
    }

    const maxScore = this.configuration.maximum_total_score;
    return 100 * (transplant.score ?? 0) / maxScore;
  }
}
