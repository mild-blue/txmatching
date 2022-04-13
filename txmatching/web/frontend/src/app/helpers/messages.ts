import { Donor, Recipient, TransplantMessages } from '@app/model';

export const countAllMessages = (data: Donor | Recipient | TransplantMessages | undefined): number => {
  if (!data?.allMessages) {
    return 0;
  }

  return data.allMessages.warning.length + data.allMessages.error.length + data.allMessages.info.length;
};

export const findMostSevereMessageType = (donor: Donor | undefined, recipient: Recipient | undefined = undefined): WarningType => {
  if (donor?.allMessages.error.length || recipient?.allMessages.error.length) {
    return 'error';
  }

  if (donor?.allMessages.warning.length || recipient?.allMessages.warning.length) {
    return 'warning';
  }

  return 'info';
};

export type WarningType = 'error' | 'warning' | 'info';
