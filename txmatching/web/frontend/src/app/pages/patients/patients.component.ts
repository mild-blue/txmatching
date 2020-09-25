import { Component, OnInit } from '@angular/core';
import { PatientList, PatientPair } from '@app/model/Patient';
import { PatientService } from '@app/services/patient/patient.service';
import { PatientPairItemComponent } from '@app/components/patient-pair-item/patient-pair-item.component';
import { PatientPairDetailComponent } from '@app/components/patient-pair-detail/patient-pair-detail.component';
import { ListItemAbstractComponent, ListItemDetailAbstractComponent } from '@app/components/list-item/list-item.interface';
import { PatientListFilter, patientListFilters, PatientListFilterType } from '@app/pages/patients/patients.interface';

@Component({
  selector: 'app-patients',
  templateUrl: './patients.component.html',
  styleUrls: ['./patients.component.scss']
})
export class PatientsComponent implements OnInit {

  public activeListFilter?: PatientListFilter;
  public listFilterTypes: typeof PatientListFilterType = PatientListFilterType;

  public patients?: PatientList;

  public pairs: PatientPair[] = [];

  private _listItemComponent: typeof ListItemAbstractComponent = PatientPairItemComponent;
  private _listItemDetailComponent: typeof ListItemDetailAbstractComponent = PatientPairDetailComponent;

  constructor(private _patientService: PatientService) {
    this.activeListFilter = patientListFilters[0];
  }

  ngOnInit(): void {
    this._initPatients();
  }

  get patientsCount(): number {
    return this.patients ? this.patients.donors.length + this.patients.recipients.length : 0;
  }

  get listItemComponent(): typeof ListItemAbstractComponent {
    return this._listItemComponent;
  }

  get listItemDetailComponent(): typeof ListItemDetailAbstractComponent {
    return this._listItemDetailComponent;
  }

  public setActiveFilter(type: PatientListFilterType): void {
    this.activeListFilter = patientListFilters.find(f => f.type === type);
  }

  private _initPatients(): void {
    this.patients = this._patientService.getLocalPatients();
    if (!this.patients) {
      return;
    }

    // add pairs
    for (const donor of this.patients.donors) {
      const recipient = this.patients.recipients.find(r => r.db_id === donor.related_recipient_db_id);

      if (!recipient) {
        continue;
      }

      this.pairs.push({
        index: this.pairs.length + 1,
        donor,
        recipient
      });
    }
  }
}
