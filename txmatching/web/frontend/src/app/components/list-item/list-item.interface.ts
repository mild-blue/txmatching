import { PatientList } from '@app/model/Patient';
import { Configuration } from '@app/model/Configuration';

export interface ListItem {
  index: number;
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
}

