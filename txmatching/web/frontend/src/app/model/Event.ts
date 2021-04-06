import { TxmEventStateGenerated } from '@app/generated';

export interface TxmEvent {
  id: number;
  name: string;
  defaultConfigId?: number;
  state: TxmEventStateGenerated;
}

export interface TxmEvents {
  events: TxmEvent[];
}
