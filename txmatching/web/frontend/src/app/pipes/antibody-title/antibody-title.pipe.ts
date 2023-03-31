import { Pipe, PipeTransform } from "@angular/core";
import { AntibodyMatch } from "@app/model/Hla";
import { AntibodyMatchType } from "@app/model";

@Pipe({
  name: "antibodyTitle",
})
export class AntibodyTitlePipe implements PipeTransform {
  transform(antibodyMatch: AntibodyMatch): string {
    const antibody = antibodyMatch.hlaAntibody;

    const secondChain = antibody.secondCode
      ? `Second High res: ${antibody.secondCode.highRes ?? "-"}\n` +
        `Second Split: ${antibody.secondCode.split ?? "-"}\n` +
        `Second Broad: ${antibody.secondCode.broad}\n\n` +
        `Second Raw code: ${antibody.secondRawCode}\n\n`
      : "";

    const antibodyDescription =
      `MFI: ${antibody.mfi}\n` +
      `Cutoff: ${antibody.cutoff}\n\n` +
      `High res: ${antibody.code.highRes ?? "-"}\n` +
      `Split: ${antibody.code.split ?? "-"}\n` +
      `Broad: ${antibody.code.broad}\n\n` +
      `Raw code: ${antibody.rawCode}\n\n` +
      secondChain +
      `Match: ${antibodyMatch.matchType !== AntibodyMatchType.NONE ? antibodyMatch.matchType : "-"}\n` +
      `Type: ${antibody.type}`;
    return antibodyDescription;
  }
}
