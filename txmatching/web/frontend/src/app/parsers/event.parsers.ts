import { TxmEventStateType } from "@app/model/enums/TxmEventStateType";
import { StrictnessTypeGenerated, TxmEventGenerated, TxmEventsGenerated, TxmEventStateGenerated } from "../generated";
import { TxmEvent, TxmEvents } from "../model/Event";
import { StrictnessType } from "@app/model/enums/StrictnessType";

export const parseTxmEvent = (data: TxmEventGenerated): TxmEvent => {
  return {
    id: data.id,
    name: data.name,
    defaultConfigId: data.default_config_id,
    state: parseTxmEventState(data.state),
    strictnessType: parseStrictnessType(data.strictness_type),
  };
};

export const parseTxmEvents = (data: TxmEventsGenerated): TxmEvents => {
  return {
    events: data.events.map(parseTxmEvent),
  };
};

export const parseTxmEventState = (data: TxmEventStateGenerated): TxmEventStateType => {
  return TxmEventStateType[data];
};

export const parseStrictnessType = (data: StrictnessTypeGenerated): StrictnessType => {
  return StrictnessType[data];
};
