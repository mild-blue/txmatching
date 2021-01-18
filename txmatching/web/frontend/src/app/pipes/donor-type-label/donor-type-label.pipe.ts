import { Pipe, PipeTransform } from '@angular/core';
import { DonorType } from '@app/model/Donor';

@Pipe({
  name: 'donorTypeLabel'
})
export class DonorTypeLabelPipe implements PipeTransform {

  transform(type: DonorType): string {
    if (type === DonorType.BRIDGING_DONOR) {
      return 'bridging donor';
    } else if (type === DonorType.NON_DIRECTED) {
      return 'non-directed donor';
    } else if (type === DonorType.DONOR) {
      return 'donor';
    }

    return type;
  }

}
