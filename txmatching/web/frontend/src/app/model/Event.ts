export interface TxmEvent {
  id: number;
  name: string;
  defaultConfigId?: number;
}

export interface TxmEvents {
  events: TxmEvent[];
}
