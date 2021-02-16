import { Component, Input, OnInit } from '@angular/core';
import { PatientEditable } from '@app/model/PatientEditable';
import { PatientSexType } from '@app/model';

@Component({
  selector: 'app-sex',
  templateUrl: './sex.component.html',
  styleUrls: ['./sex.component.scss']
})
export class SexComponent implements OnInit {

  @Input() patient?: PatientEditable;
  public allSexes: PatientSexType[] = Object.values(PatientSexType);

  constructor() {
  }

  ngOnInit(): void {
  }

}
