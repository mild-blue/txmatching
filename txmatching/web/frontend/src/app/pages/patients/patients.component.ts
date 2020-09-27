import { Component, OnInit } from '@angular/core';
import { PatientList, PatientPair } from '@app/model/Patient';
import { PatientService } from '@app/services/patient/patient.service';
import { ListItem } from '@app/components/list-item/list-item.interface';
import { PatientListFilter, patientListFilters, PatientListFilterType } from '@app/pages/patients/patients.interface';

@Component({
  selector: 'app-patients',
  templateUrl: './patients.component.html',
  styleUrls: ['./patients.component.scss']
})
export class PatientsComponent implements OnInit {

  public activeListFilter?: PatientListFilter;
  public listFilterTypes: typeof PatientListFilterType = PatientListFilterType;
  public tabs: string[] = Object.values(PatientListFilterType);

  public patients?: PatientList;
  public pairs: PatientPair[] = [];

  constructor(private _patientService: PatientService) {
    this.activeListFilter = patientListFilters[0];
  }

  ngOnInit(): void {
    this._initPatients();
  }

  get patientsCount(): number {
    return this.patients ? this.patients.donors.length + this.patients.recipients.length : 0;
  }

  public setActiveFilter(type: string): void {
    this.activeListFilter = patientListFilters.find(f => String(f.type) === type);
  }

  public getFilteredItems(): ListItem[] {
    if (this.activeListFilter && this.patients) {
      if (this.activeListFilter.type === PatientListFilterType.Donors) {
        return this.patients.donors;
      }
      if (this.activeListFilter.type === PatientListFilterType.Recipients) {
        return this.patients.recipients;
      }
    }

    return this.pairs;
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
        d: donor,
        r: recipient
      });
    }

    // add indexes for list rendering
    this.patients.donors.map((d, key) => {
      d.index = key + 1;
      return d;
    });

    this.patients.recipients.map((r, key) => {
      r.index = key + 1;
      return r;
    });
  }
}
