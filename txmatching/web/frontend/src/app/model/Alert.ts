import * as uuid from 'uuid';

export enum AlertType {
  Success,
  Error,
  Info,
  Warning
}

export class Alert {
  uuid: string;
  id?: string;
  type?: AlertType;
  message?: string;
  fade?: boolean;

  constructor(init?: Partial<Alert>) {
    this.uuid = uuid.v4();
    Object.assign(this, init);
  }
}

export const fadeDurationMs = 5000;
