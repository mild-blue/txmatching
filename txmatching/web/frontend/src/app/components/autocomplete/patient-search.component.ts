import { Component, EventEmitter, Input, OnInit, Output } from '@angular/core';
import { Patient, patientNameProperty } from '@app/model/Patient';

@Component({
  selector: 'app-patient-search',
  templateUrl: './patient-search.component.html',
  styleUrls: ['./patient-search.component.scss']
})
export class PatientSearchComponent implements OnInit {

  @Input() patients: Patient[] = [];
  @Output() selected: EventEmitter<number> = new EventEmitter<number>();

  public keyword = patientNameProperty;

  constructor() {
  }

  ngOnInit(): void {
  }

  selectEvent(item: Patient) {
    this.selected.emit(item.db_id);
  }
}
