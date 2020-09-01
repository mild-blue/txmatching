import { Component, Input, OnInit } from '@angular/core';
import { MatchingView } from '@app/model/Matching';
import { Patient } from '@app/model/Patient';

@Component({
  selector: 'app-matching-detail',
  templateUrl: './matching-detail.component.html',
  styleUrls: ['./matching-detail.component.scss']
})
export class MatchingDetailComponent implements OnInit {

  @Input() matching?: MatchingView;
  @Input() patients: Patient[] = [];

  constructor() {
  }

  ngOnInit(): void {
  }

}
