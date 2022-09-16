import { Component, Input } from "@angular/core";
import { LoadingIconSize } from "@app/components/loading-icon/loading-icon.interface";

@Component({
  selector: "app-loading",
  templateUrl: "./loading.component.html",
  styleUrls: ["./loading.component.scss"],
})
export class LoadingComponent {
  @Input() show: boolean = false;
  public iconSize = LoadingIconSize.large;
}
