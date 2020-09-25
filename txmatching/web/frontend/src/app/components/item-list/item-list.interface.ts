import { PatientList } from '@app/model/Patient';
import { Configuration } from '@app/model/Configuration';

export interface ListItem {
  index: number;
}

export class ListItemView {
  constructor(public itemData: any,
              public detailData: any) {
  }
}

export class ListItemDetailView {
  constructor(public data: any) {
  }
}

export class ListItemComponent {
  data?: any;
  isActive?: boolean;
  patients?: PatientList;
  configuration?: Configuration;
}

export class ListItemDetailComponent {
  data?: any;
  patients?: PatientList;
}

