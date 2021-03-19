import { TxmEventGenerated, TxmEventsGenerated } from '../generated';
import { TxmEvent, TxmEvents } from '../model/Event';

export const parseTxmEvent = (data: TxmEventGenerated): TxmEvent => {
  return {
    id: data.id,
    name: data.name,
    defaultConfigId: data.default_config_id
  };
};

export const parseTxmEvents = (data: TxmEventsGenerated): TxmEvents => {
  return {
    events: data.events.map(parseTxmEvent)
  };
};
