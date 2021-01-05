import { Component, OnInit } from '@angular/core';
import { VersionService } from '@app/services/version/version.service';
import { EnvironmentType, Version } from '@app/model/Version';

@Component({
  selector: 'app-logo',
  templateUrl: './logo.component.html',
  styleUrls: ['./logo.component.scss']
})
export class LogoComponent implements OnInit {

  _version: Version | null;

  constructor(
    private _versionService: VersionService
  ) {
    this._version = _versionService.getVersion();
  }

  ngOnInit(): void {
  }

  public getVersionString(): string {
    if (!this._version) {
      return '';
    }

    let e = this._version.environment;
    let v = this._version.version;
    let vShort = v.substr(0, 7);

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
