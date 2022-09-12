import { Component, Input, OnInit } from "@angular/core";
import { faSpinner } from "@fortawesome/free-solid-svg-icons";
import { LoadingIconSize } from "@app/components/loading-icon/loading-icon.interface";

@Component({
  selector: "app-loading-icon",
  templateUrl: "./loading-icon.component.html",
  styleUrls: ["./loading-icon.component.scss"],
})
export class LoadingIconComponent {
  @Input() size: LoadingIconSize = LoadingIconSize.medium;
  public icon = faSpinner;
}
