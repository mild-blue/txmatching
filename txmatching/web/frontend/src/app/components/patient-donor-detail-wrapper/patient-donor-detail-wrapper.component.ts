import { Component, Input, OnInit } from '@angular/core';
import { ListItemDetailAbstractComponent } from '@app/components/list-item/list-item.interface';
import { PatientList } from '@app/model/PatientList';
import { Configuration } from '@app/model/Configuration';
import { PatientDonorTab } from '@app/components/patient-donor-detail-wrapper/patient-donor-detail-wrapper.interface';
import { Donor } from '@app/model/Donor';

@Component({
  selector: 'app-patient-donor-detail-wrapper',
  templateUrl: './patient-donor-detail-wrapper.component.html',
  styleUrls: ['./patient-donor-detail-wrapper.component.scss']
})
export class PatientDonorDetailWrapperComponent extends ListItemDetailAbstractComponent implements OnInit {

  @Input() item?: Donor;
  @Input() patients?: PatientList;
  @Input() configuration?: Configuration;

  public activeTab: PatientDonorTab = PatientDonorTab.Overview;
  public tabs: typeof PatientDonorTab = PatientDonorTab;
  public tabNames: string[] = Object.values(PatientDonorTab);

  constructor() {
    super();
  }

  ngOnInit(): void {
  }

  public setActiveTab(tab: string): void {
    this.activeTab = Object.values(this.tabs).find(t => t === tab) as PatientDonorTab;
  }
}
