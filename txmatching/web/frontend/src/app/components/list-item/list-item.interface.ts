import { PatientList } from '@app/model/Patient';
import { Configuration } from '@app/model/Configuration';

export interface ListItem {
  index: number;
}

export class ListItemAbstractComponent {
  data?: any;
  isActive?: boolean;
  patients?: PatientList;
  configuration?: Configuration;
}

export class ListItemDetailAbstractComponent {
  data?: any;
  patients?: PatientList;
}

