import { Configuration } from '@app/model/Configuration';
import { PatientService } from '@app/services/patient/patient.service';
import { UiInteractionsService } from '@app/services/ui-interactions/ui-interactions.service';
import { PatientList } from '@app/model/PatientList';

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

  constructor(_patientService?: PatientService,
              _uiInteractionsService?: UiInteractionsService) {
  }
}

// HACK: instead of using this, create proper ListItem in all places
// where this cons is used
export const DEFAULT_LIST_ITEM: ListItem =  {
  index: 0,
  isActive: undefined,
  itemComponent: ListItemAbstractComponent,
  detailComponent: ListItemDetailAbstractComponent
}
