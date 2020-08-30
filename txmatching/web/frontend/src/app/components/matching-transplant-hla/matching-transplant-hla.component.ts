import { Component, Input, OnInit } from '@angular/core';
import { Patient, PatientType } from '@app/model/Patient';

@Component({
  selector: 'app-matching-transplant-hla',
  templateUrl: './matching-transplant-hla.component.html',
  styleUrls: ['./matching-transplant-hla.component.scss']
})
export class MatchingTransplantHlaComponent implements OnInit {

  @Input() patient?: Patient;
  @Input() matchingAntigens: string[] = [];
  @Input() antigenPrefix: string = '';

  public PatientType: typeof PatientType = PatientType;

  constructor() {
  }

  ngOnInit(): void {
  }

  get isRecipient(): boolean {
    return this.patient ? this.patient.patient_type === PatientType.RECIPIENT.valueOf() : false;
  }

  public filteredCodes(codes?: string[]): string[] {
    return codes ? codes.filter(code => code.startsWith(this.antigenPrefix)) : [];
  }
}
