import { Donor, Recipient } from '@app/model';

export const countAllMessages = (data: Donor | Recipient | undefined): number => {
  if (!data?.all_messages) {
    return 0;
  }

  return data.all_messages.warning.length + data.all_messages.error.length + data.all_messages.info.length;
};

export const findMostSevereMessageType = (donor: Donor | undefined, recipient: Recipient | undefined = undefined): WarningType => {
  if (donor?.all_messages.error.length || recipient?.all_messages.error.length) {
    return 'error';
  }

  if (donor?.all_messages.warning.length || recipient?.all_messages.warning.length) {
    return 'warning';
  }

  return 'info';
};

export type WarningType = 'error' | 'warning' | 'info';
