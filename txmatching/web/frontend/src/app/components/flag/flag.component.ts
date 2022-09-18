import { Component, Input, OnInit } from "@angular/core";

@Component({
  selector: "app-flag",
  templateUrl: "./flag.component.html",
  styleUrls: ["./flag.component.scss"],
})
export class FlagComponent implements OnInit {
  @Input() countryCode?: string;
  public countryParts: string[] = [];

  constructor() {}

  ngOnInit() {
    if (this.countryCode) {
      this.countryParts = this.countryCode.split("_");
    }
  }

  get image(): string {
    return `../../../assets/img/countries/${this.countryParts[0]}.png`;
  }
}
