import { Component, Input, OnInit } from '@angular/core';
import { Round, Transplant } from '@app/model/Matching';
import { compatibleBloodGroups, Patient } from '@app/model/Patient';
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
  @Input() patients: Patient[] = [];
  @Input() configuration?: AppConfiguration;

  public arrowRight = faAngleRight;

  constructor() {
  }

  get roundIndex(): string {
    return '';
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

  public donor(transplant: Transplant): Patient | undefined {
    return this.patients.find(p => p.medical_id === transplant.donor);
  }

  public recipient(transplant: Transplant): Patient | undefined {
    return this.patients.find(p => p.medical_id === transplant.recipient);
  }

  public percentageScore(transplant: Transplant): number {
    if (!this.configuration) {
      return 0;
    }

    const maxScore = this.configuration.maximum_total_score;
    return 100 * transplant.score / maxScore;
  }
}
