import { Component, EventEmitter, Input, Output } from '@angular/core';
import { Patient, patientNameProperty } from '@app/model/Patient';

@Component({
  selector: 'app-patient-search',
  templateUrl: './patient-search.component.html',
  styleUrls: ['./patient-search.component.scss']
})
export class PatientSearchComponent {

  @Input() patients: Patient[] = [];
  @Input() value?: string;

  @Output() selected: EventEmitter<number> = new EventEmitter<number>();

  public keyword = patientNameProperty;

  selectEvent(item: Patient) {
    this.selected.emit(item.db_id);
  }
}
