import { Pipe, PipeTransform } from '@angular/core';
import { Antigen } from '@app/model';

@Pipe({
  name: 'antigenTitle'
})
export class AntigenTitlePipe implements PipeTransform {

  transform(antigen: Antigen): string {
    return `High res: ${antigen.code.highRes ?? '-'}\n`+
      `Split: ${antigen.code.split ?? '-'}\n`+
      `Broad: ${antigen.code.broad}\n`+
      `Raw code: ${antigen.raw_code}`;
  }

}
