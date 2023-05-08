import { Component, Input } from "@angular/core";
import { PatientService } from "@app/services/patient/patient.service";
import { Configuration } from "@app/model/Configuration";
import { AntibodyMatch, DetailedScorePerGroup } from "@app/model/Hla";
import { Recipient, RecipientRequirements } from "@app/model/Recipient";
import { Donor } from "@app/model/Donor";
import { Patient } from "@app/model/Patient";
import { PatientPairStyle } from "@app/components/patient-pair/patient-pair.interface";
import { AntigenMatchType } from "@app/model/enums/AntigenMatchType";
import { AntibodyMatchType } from "@app/model/enums/AntibodyMatchType";
import { HlaAntibodyType } from "@app/model/enums/HlaAntibodyType";

@Component({
  selector: "app-matching-transplant",
  templateUrl: "./matching-transplant.component.html",
  styleUrls: ["./matching-transplant.component.scss"],
})
export class MatchingTransplantComponent {
  @Input() configuration?: Configuration;

  @Input() score?: number;
  @Input() maxScore?: number;
  @Input() donor?: Donor;
  @Input() recipient?: Recipient;
  @Input() isBloodCompatible?: boolean;
  @Input() hasCrossmatch: boolean = false;
  @Input() detailedScorePerGroup?: DetailedScorePerGroup[];
  @Input() globalMessage: string = "";

  public patientPairStyles = PatientPairStyle;

  constructor(private _patientService: PatientService) {}

  public getAntigenMatchClass(match: AntigenMatchType): string {
    if (match === AntigenMatchType.BROAD || match === AntigenMatchType.HIGH_RES || match === AntigenMatchType.SPLIT) {
      // donor antigen matches some recipient antigen
      return "matching";
    }

    return "";
  }

  public getAntibodyClass(match: AntibodyMatch): string {
    var classes = "";
    if (match.matchType !== AntibodyMatchType.NONE) {
      // recipient antibody matches some donor antigen
      classes = classes.concat("bad-matching");
    }

    if (match.hlaAntibody.type == HlaAntibodyType.THEORETICAL) {
      classes = classes.concat(" theoretical-antibody");
    }

    return classes;
  }

  public getPatientHeightAndWeight(patient: Patient): string | null {
    let h = patient.parameters.height;
    let w = patient.parameters.weight;

    if (h && w) {
      return `${h}/${w}`;
    } else if (h) {
      return `${h}/-`;
    } else if (w) {
      return `-/${w}`;
    } else {
      return null;
    }
  }

  public showRecipientRequirementsInfo(requirements?: RecipientRequirements): boolean {
    return (
      requirements !== undefined &&
      (requirements.requireCompatibleBloodGroup ||
        requirements.requireBetterMatchInCompatibilityIndex ||
        requirements.requireBetterMatchInCompatibilityIndexOrBloodGroup)
    );
  }

  public getRecipientRequirementsInfo(requirements?: RecipientRequirements): string {
    return (
      `${requirements?.requireCompatibleBloodGroup ? "YES" : "NO"}/` +
      `${requirements?.requireBetterMatchInCompatibilityIndex ? "YES" : "NO"}/` +
      `${requirements?.requireBetterMatchInCompatibilityIndexOrBloodGroup ? "YES" : "NO"}`
    );
  }

  public getRecipientRequirementsInfoTooltip(requirements?: RecipientRequirements): string {
    return (
      "Matching conditions\n\n" +
      `Require compatible blood group: ${requirements?.requireCompatibleBloodGroup ? "YES" : "NO (default)"}\n\n` +
      `Require new donor having better CI match than original donor: ${
        requirements?.requireBetterMatchInCompatibilityIndex ? "YES" : "NO (default)"
      }\n\n` +
      `Require new donor having better CI match than original donor or blood group match: ${
        requirements?.requireBetterMatchInCompatibilityIndexOrBloodGroup ? "YES" : "NO (default)"
      }`
    );
  }
}
