import { Component, Input, OnInit } from '@angular/core';
import { MatchingView } from '@app/model/Matching';
import { PatientList } from '@app/model/Patient';
import { ListItemDetailComponent } from '@app/components/item-list/item-list.interface';

@Component({
  selector: 'app-matching-detail',
  templateUrl: './matching-detail.component.html',
  styleUrls: ['./matching-detail.component.scss']
})
export class MatchingDetailComponent implements OnInit, ListItemDetailComponent {

  @Input() data?: MatchingView;
  @Input() patients?: PatientList;

  constructor() {
  }

  ngOnInit(): void {
  }

}
