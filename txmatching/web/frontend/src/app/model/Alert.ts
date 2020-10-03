export enum AlertType {
  Success,
  Error,
  Info,
  Warning
}

export class Alert {
  id?: string;
  type?: AlertType;
  message?: string;
  fade?: boolean;

  constructor(init?: Partial<Alert>) {
    Object.assign(this, init);
  }
}

export const alertTimeoutMs = 5000;
export const fadeDurationMs = 250;
