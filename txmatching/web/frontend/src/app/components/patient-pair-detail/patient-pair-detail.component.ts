import { Component, Input, OnInit } from "@angular/core";
import { ListItemDetailAbstractComponent } from "@app/components/list-item/list-item.interface";
import { PatientPairTab } from "@app/components/patient-pair-detail/patient-pair-detail.interface";
import { Configuration } from "@app/model/Configuration";
import { PatientPair } from "@app/model/PatientPair";
import { PatientList } from "@app/model/PatientList";
import { TxmEvent } from "@app/model/Event";
import { PatientService } from "@app/services/patient/patient.service";
import { ConfigurationService } from "@app/services/configuration/configuration.service";
import { RecipientCompatibilityInfo } from "@app/model/RecipientCompatibilityInfo";
import { UiInteractionsService } from "@app/services/ui-interactions/ui-interactions.service";
import { Donor } from "@app/model";
import { RecipientDonorCompatibilityDetail } from "@app/model/RecipientDonorCompatibilityDetail";

@Component({
  selector: "app-patient-pair-detail",
  templateUrl: "./patient-pair-detail.component.html",
  styleUrls: ["./patient-pair-detail.component.scss"],
})
export class PatientPairDetailComponent extends ListItemDetailAbstractComponent implements OnInit {
  @Input() item?: PatientPair;
  @Input() patients?: PatientList;
  @Input() configuration?: Configuration;
  @Input() defaultTxmEvent?: TxmEvent;

  public activeTab: PatientPairTab = PatientPairTab.Overview;
  public tabs: typeof PatientPairTab = PatientPairTab;
  public tabNames: string[] = Object.values(PatientPairTab);
  public recipientCompatibilityInfo?: RecipientCompatibilityInfo;
  public donorToCompatibilityInfo?: [Donor, RecipientDonorCompatibilityDetail][];

  constructor(
    private _patientsService: PatientService,
    private _configService: ConfigurationService,
    private _uiInteractionsService: UiInteractionsService
  ) {
    super();
  }

  ngOnInit(): void {
    if (this.item?.r && this.defaultTxmEvent && this.configuration && this.patients) {
      this.getRecipientCompatibilityInfo(
        this.item.r.dbId,
        this.defaultTxmEvent.id,
        this.configuration,
        this.patients.donors
      );
    }
  }

  private async getRecipientCompatibilityInfo(
    recipientId: number,
    TxmEventId: number,
    configuration: Configuration,
    donors: Donor[]
  ): Promise<void> {
    const response = await this._configService.findConfigurationId(TxmEventId, configuration);
    const configurationId = response.configId;
    const recipientCompatibilityInfo = await this._patientsService.getRecipientCompatbileDonorsAndCPRA(
      TxmEventId,
      configurationId,
      recipientId
    );
    this.recipientCompatibilityInfo = recipientCompatibilityInfo;
    const donorToCompatibilityInfo: [Donor, RecipientDonorCompatibilityDetail][] = [];

    recipientCompatibilityInfo.compatibleDonors.forEach((id) => {
      const donor = donors.find((d) => d.dbId === id);
      const detail = recipientCompatibilityInfo.compatibleDonorsDetails.find((ci) => ci.donorDbId === id);

      if (donor && detail) {
        donorToCompatibilityInfo.push([donor, detail]);
      }
    });

    this.donorToCompatibilityInfo = donorToCompatibilityInfo;
  }

  public setActiveTab(tab: string): void {
    this.activeTab = Object.values(this.tabs).find((t) => t === tab) as PatientPairTab;
  }
}
