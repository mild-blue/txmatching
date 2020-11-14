import { Component, Input, OnInit } from '@angular/core';
import { ListItemDetailAbstractComponent } from '@app/components/list-item/list-item.interface';
import { PatientPairTab } from '@app/components/patient-pair-detail/patient-pair-detail.interface';
import { Configuration } from '@app/model/Configuration';
import { PatientPair } from '@app/model/PatientPair';
import { PatientList } from '@app/model/PatientList';

@Component({
  selector: 'app-patient-pair-detail',
  templateUrl: './patient-pair-detail.component.html',
  styleUrls: ['./patient-pair-detail.component.scss']
})
export class PatientPairDetailComponent extends ListItemDetailAbstractComponent implements OnInit {

  @Input() item?: PatientPair;
  @Input() patients?: PatientList;
  @Input() configuration?: Configuration;

  public activeTab: PatientPairTab = PatientPairTab.Pair;
  public tabs: typeof PatientPairTab = PatientPairTab;
  public tabNames: string[] = Object.values(PatientPairTab);

  constructor() {
    super();
  }

  ngOnInit(): void {
  }

  public setActiveTab(tab: string): void {
    this.activeTab = Object.values(this.tabs).find(t => t === tab) as PatientPairTab;
  }

}
