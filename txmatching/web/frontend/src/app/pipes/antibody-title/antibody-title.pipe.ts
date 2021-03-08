import { Pipe, PipeTransform } from '@angular/core';
import { Antibody } from '@app/model/Hla';

@Pipe({
  name: 'antibodyTitle'
})
export class AntibodyTitlePipe implements PipeTransform {

  transform(antibody: Antibody): string {
    return `MFI: ${antibody.mfi}\n`+
      `Cutoff: ${antibody.cutoff}\n\n`+
      `High res: ${antibody.code.highRes ?? '-'}\n`+
      `Split: ${antibody.code.split ?? '-'}\n`+
      `Broad: ${antibody.code.broad}\n`+
      `Raw code: ${antibody.raw_code}`;
  }

}
