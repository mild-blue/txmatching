import { Component, Input, OnInit } from '@angular/core';
import { Round, Transplant } from '@app/model/Matching';
import { compatibleBloodGroups, Donor, Recipient, PatientList, DonorType } from '@app/model/Patient';
import { faAngleRight } from '@fortawesome/free-solid-svg-icons';
import { AppConfiguration } from '@app/model/Configuration';

@Component({
  selector: 'app-matching-round',
  templateUrl: './matching-round.component.html',
  styleUrls: ['./matching-round.component.scss']
})
export class MatchingRoundComponent implements OnInit {

  @Input() round?: Round;
  @Input() index: number = 0;
  @Input() patients?: PatientList;
  @Input() configuration?: AppConfiguration;

  public arrowRight = faAngleRight;

  constructor() {
  }

  get roundIndex(): string {
    const roundIndex = `${this.index}`;
    if (!this.round || !this.round.transplants.length) {
      return roundIndex;
    }

    const firstTransplant = this.round.transplants[0];
    const donor = this.donor(firstTransplant);

    if (donor) {
      if (donor.donor_type === DonorType.BRIDGING_DONOR.valueOf()) {
        return `${roundIndex}B`;
      }
      if (donor.donor_type === DonorType.ALTRUIST.valueOf()) {
        return `${roundIndex}A`;
      }
    }

    return roundIndex;
  }

  ngOnInit(): void {
  }

  public isDonorBloodCompatible(transplant: Transplant): boolean {

    const donor = this.donor(transplant);
    const recipient = this.recipient(transplant);

    if (!donor || !recipient) {
      return false;
    }

    const donorBloodGroup = donor.parameters.blood_group;
    const recipientBloodGroup = recipient.parameters.blood_group;
    return compatibleBloodGroups[recipientBloodGroup].includes(donorBloodGroup);
  }

  public donor(transplant: Transplant): Donor | undefined {
    return this.patients?.donors.find(p => p.medical_id === transplant.donor);
  }

  public recipient(transplant: Transplant): Recipient | undefined {
    return this.patients?.recipients.find(p => p.medical_id === transplant.recipient);
  }

  public percentageScore(transplant: Transplant): number {
    if (!this.configuration) {
      return 0;
    }

    const maxScore = this.configuration.maximum_total_score;
    return 100 * transplant.score / maxScore;
  }
}
