import { Component, Input, OnInit } from '@angular/core';
import { PatientEditable } from '@app/model/PatientEditable';
import { separatorKeysCodes } from '@app/directives/validators/form.directive';

@Component({
  selector: 'app-antigens',
  templateUrl: './antigens.component.html',
  styleUrls: ['./antigens.component.scss']
})
export class AntigensComponent implements OnInit {

  @Input() patient?: PatientEditable;
  public separatorKeysCodes: number[] = separatorKeysCodes;

  constructor() {
  }

  ngOnInit(): void {
  }

  public addAntigen(patient: PatientEditable, code: string, control: HTMLInputElement): void {
    if (!code) {
      return;
    }

    patient.addAntigen(code);

    // Reset input
    control.value = '';
  }

}
