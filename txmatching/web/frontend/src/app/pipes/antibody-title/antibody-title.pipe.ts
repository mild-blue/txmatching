import { Pipe, PipeTransform } from '@angular/core';
import { AntibodyMatch } from '@app/model/Hla';
import { AntibodyMatchType } from '@app/model';

@Pipe({
  name: 'antibodyTitle'
})
export class AntibodyTitlePipe implements PipeTransform {

  transform(antibodyMatch: AntibodyMatch): string {
    const antibody = antibodyMatch.hla_antibody;
    return `MFI: ${antibody.mfi}\n`+
      `Cutoff: ${antibody.cutoff}\n\n`+
      `High res: ${antibody.code.highRes ?? '-'}\n`+
      `Split: ${antibody.code.split ?? '-'}\n`+
      `Broad: ${antibody.code.broad}\n\n`+
      `Raw code: ${antibody.raw_code}\n\n`+
      `Match: ${antibodyMatch.match_type !== AntibodyMatchType.NONE ? antibodyMatch.match_type : '-'}`;
  }

}
