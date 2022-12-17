import { TxmEventStateGenerated, StrictnessTypeGenerated } from '@app/generated';

export interface TxmEvent {
  id: number;
  name: string;
  defaultConfigId?: number;
  state: TxmEventStateGenerated;
  strictness_type: StrictnessTypeGenerated;
}

export interface TxmEvents {
  events: TxmEvent[];
}
