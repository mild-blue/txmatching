import { PatientList } from '@app/model/Patient';

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

export interface ListItemDetailComponent {
  data?: any;
  patients?: PatientList;
}

