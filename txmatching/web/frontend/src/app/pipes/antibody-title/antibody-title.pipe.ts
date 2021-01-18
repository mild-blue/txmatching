import { Pipe, PipeTransform } from '@angular/core';
import { Antibody } from '@app/model/Hla';

@Pipe({
  name: 'antibodyTitle'
})
export class AntibodyTitlePipe implements PipeTransform {

  transform(antibody: Antibody): string {
    return `Raw code: ${antibody.raw_code}\nMFI: ${antibody.mfi}\nCutoff: ${antibody.cutoff}`
  }

}
