import { Configuration } from '@app/model/Configuration';
import { PatientService } from '@app/services/patient/patient.service';
import { PatientList } from '@app/model/PatientList';

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

  constructor(_patientService?: PatientService) {
  }
}

