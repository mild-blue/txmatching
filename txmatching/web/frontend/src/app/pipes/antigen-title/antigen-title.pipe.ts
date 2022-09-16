import { Pipe, PipeTransform } from "@angular/core";
import { AntigenMatch, AntigenMatchType } from "@app/model";

@Pipe({
  name: "antigenTitle",
})
export class AntigenTitlePipe implements PipeTransform {
  transform(antigenMatch: AntigenMatch): string {
    const antigen = antigenMatch.hlaType;
    return (
      `High res: ${antigen.code.highRes ?? "-"}\n` +
      `Split: ${antigen.code.split ?? "-"}\n` +
      `Broad: ${antigen.code.broad ?? "-"}\n\n` +
      `Raw code: ${antigen.rawCode}\n\n` +
      `Match: ${antigenMatch.matchType !== AntigenMatchType.NONE ? antigenMatch.matchType : "-"}`
    );
  }
}
