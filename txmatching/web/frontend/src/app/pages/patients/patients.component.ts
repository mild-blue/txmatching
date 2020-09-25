import { Component, OnInit } from '@angular/core';
import { PatientList, PatientPair } from '@app/model/Patient';
import { PatientService } from '@app/services/patient/patient.service';
import { PatientPairItemComponent } from '@app/components/patient-pair-item/patient-pair-item.component';
import { PatientPairDetailComponent } from '@app/components/patient-pair-detail/patient-pair-detail.component';

@Component({
  selector: 'app-patients',
  templateUrl: './patients.component.html',
  styleUrls: ['./patients.component.scss']
})
export class PatientsComponent implements OnInit {

  public patients?: PatientList;
  public pairs: PatientPair[] = [];

  public listItemComponent: typeof PatientPairItemComponent = PatientPairItemComponent;
  public listItemDetailComponent: typeof PatientPairDetailComponent = PatientPairDetailComponent;

  constructor(private _patientService: PatientService) {
  }

  ngOnInit(): void {
    this._initPatients();
  }

  get patientsCount(): number {
    return this.patients ? this.patients.donors.length + this.patients.recipients.length : 0;
  }

  private _initPatients(): void {
    this.patients = this._patientService.getLocalPatients();
    if (!this.patients) {
      return;
    }

    let index = 1;
    for (const donor of this.patients.donors) {
      const recipient = this.patients.recipients.find(r => r.db_id === donor.related_recipient_db_id);

      if (!recipient) {
        continue;
      }

      this.pairs.push({
        index,
        donor,
        recipient
      });

      index++;
    }
  }
}
