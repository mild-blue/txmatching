import { Component, Input, OnInit } from '@angular/core';
import { MatchingView } from '@app/model/Matching';

@Component({
  selector: 'app-matching-detail',
  templateUrl: './matching-detail.component.html',
  styleUrls: ['./matching-detail.component.scss']
})
export class MatchingDetailComponent implements OnInit {

  @Input() matching?: MatchingView;

  constructor() {
  }

  ngOnInit(): void {
  }

}
