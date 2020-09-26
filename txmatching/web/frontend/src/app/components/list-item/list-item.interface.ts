import { PatientList } from '@app/model/Patient';
import { Configuration } from '@app/model/Configuration';
import { PatientService } from '@app/services/patient/patient.service';

export interface ListItem {
  index: number;
}

export class ListItemAbstractComponent {
  item?: ListItem;
  patients?: PatientList;
  configuration?: Configuration;
}

export class ListItemDetailAbstractComponent {
  item?: ListItem;
  patients?: PatientList;

  constructor(_patientService?: PatientService) {
  }
}

