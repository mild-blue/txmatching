import { Configuration } from "@app/model/Configuration";
import { PatientService } from "@app/services/patient/patient.service";
import { UiInteractionsService } from "@app/services/ui-interactions/ui-interactions.service";
import { PatientList } from "@app/model/PatientList";
import { TxmEvent } from "@app/model/Event";
import { ConfigurationService } from "@app/services/configuration/configuration.service";

export interface ListItem {
  index: number;
  isActive?: boolean;
  itemComponent: typeof ListItemAbstractComponent;
  detailComponent: typeof ListItemDetailAbstractComponent;
}

export class ListItemAbstractComponent {
  item?: ListItem;
  isActive?: boolean;
  patients?: PatientList;
  configuration?: Configuration;
}

export class ListItemDetailAbstractComponent {
  item?: ListItem;
  patients?: PatientList;
  configuration?: Configuration;
  defaultTxmEvent?: TxmEvent;

  constructor(
    _patientService?: PatientService,
    _configService?: ConfigurationService,
    _uiInteractionsService?: UiInteractionsService
  ) {}
}
