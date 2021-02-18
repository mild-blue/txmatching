import { Component, Input, OnInit } from '@angular/core';
import { PatientEditable } from '@app/model/PatientEditable';
import { Sex } from '@app/model';

@Component({
  selector: 'app-sex',
  templateUrl: './sex.component.html',
  styleUrls: ['./sex.component.scss']
})
export class SexComponent implements OnInit {

  @Input() patient?: PatientEditable;
  public allSexes: Sex[] = Object.values(Sex);

  constructor() {
  }

  ngOnInit(): void {
  }

}
