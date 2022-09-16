import { Component, Input } from "@angular/core";
import { WarningType } from "@app/helpers/messages";

@Component({
  selector: "app-warning",
  templateUrl: "./warning.component.html",
  styleUrls: ["./warning.component.scss"],
})
export class WarningComponent {
  @Input() warningType: WarningType = "info";
  @Input() data?: string[];

  constructor() {}
}
