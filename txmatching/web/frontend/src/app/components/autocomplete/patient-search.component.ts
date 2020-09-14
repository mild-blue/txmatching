import { Component, Input, OnInit } from '@angular/core';
import { Patient, patientNameProperty } from '@app/model/Patient';

@Component({
  selector: 'app-patient-search',
  templateUrl: './patient-search.component.html',
  styleUrls: ['./patient-search.component.scss']
})
export class PatientSearchComponent implements OnInit {

  @Input() patients: Patient[] = [];

  public keyword = patientNameProperty;

  constructor() {
  }

  ngOnInit(): void {
  }

  selectEvent(item: Patient) {
    console.log('selected', item);
    // do something with selected item
  }
}
