import { Component, OnInit } from "@angular/core";
import { VersionService } from "@app/services/version/version.service";
import { Version } from "@app/model/Version";
import { EnvironmentType } from "@app/model/enums/EnvironmentType";

@Component({
  selector: "app-logo",
  templateUrl: "./logo.component.html",
  styleUrls: ["./logo.component.scss"],
})
export class LogoComponent implements OnInit {
  private _version?: Version;

  constructor(private _versionService: VersionService) {
    this._version = _versionService.getVersion();
  }

  ngOnInit(): void {}

  public getVersionString(): string {
    if (!this._version) {
      return "";
    }

    const e = this._version.environment;
    const v = this._version.version;
    const vShort = v.substr(0, 7);

    switch (e) {
      case EnvironmentType.PRODUCTION:
        return v;
      case EnvironmentType.STAGING:
        return `${vShort} (S)`;
      case EnvironmentType.DEVELOPMENT:
        return `${vShort} (D)`;
      default:
        return `${v} (${e})`;
    }
  }
}
