import * as uuid from 'uuid';
import { AlertType } from '@app/model/enums/AlertType';

export class Alert {
  uuid: string;
  id?: string;
  type?: AlertType;
  message?: string;
  fade?: boolean;
  action?: Function;
  actionLabel?: string;
  fadeAutomatically?: boolean;

  constructor(init?: Partial<Alert>) {
    this.uuid = uuid.v4();
    Object.assign(this, init);
  }
}

export const fadeDurationMs = 5000;
