import { PatientList } from '@app/model/Patient';
import { Configuration } from '@app/model/Configuration';
import { PatientService } from '@app/services/patient/patient.service';
import { UiInteractionsService } from '@app/services/ui-interactions/ui-interactions.service';

export interface ListItem {
  index: number;
  isActive?: boolean;
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

  constructor(_patientService?: PatientService,
              _uiInteractionsService?: UiInteractionsService) {
  }
}

