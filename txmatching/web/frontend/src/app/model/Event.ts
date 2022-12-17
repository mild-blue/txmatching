import { StrictnessType } from "@app/model/enums/StrictnessType";
import { TxmEventStateType } from "@app/model/enums/TxmEventStateType";

export interface TxmEvent {
  id: number;
  name: string;
  defaultConfigId?: number;
  state: TxmEventStateType;
  strictnessType: StrictnessType;
}

export interface TxmEvents {
  events: TxmEvent[];
}
