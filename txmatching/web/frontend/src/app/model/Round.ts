import { Transplant } from "@app/model/Transplant";
import { DonorType } from "@app/model/enums/DonorType";

export interface Round {
  index: string;
  donorType: DonorType;
  transplants: Transplant[];
}
