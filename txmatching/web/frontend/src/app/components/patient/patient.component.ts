import { Component, Input } from "@angular/core";
import { Patient } from "@app/model/Patient";

@Component({
  selector: "patient",
  templateUrl: "./patient.component.html",
  styleUrls: ["./patient.component.scss"],
})
export class PatientComponent {
  @Input() patient?: Patient;
}
