import { Component, Input, OnInit } from "@angular/core";

@Component({
  selector: "app-setting-item",
  templateUrl: "./setting-item.component.html",
  styleUrls: ["./setting-item.component.scss"],
})
export class SettingItemComponent implements OnInit {
  @Input() label?: string;
  @Input() required?: boolean;

  constructor() {}

  ngOnInit(): void {}
}
