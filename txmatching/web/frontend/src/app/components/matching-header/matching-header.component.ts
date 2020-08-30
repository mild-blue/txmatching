import { Component, Input, OnInit } from '@angular/core';
import { MatchingView } from '@app/model/Matching';

@Component({
  selector: 'app-matching-header',
  templateUrl: './matching-header.component.html',
  styleUrls: ['./matching-header.component.scss']
})
export class MatchingHeaderComponent implements OnInit {

  @Input() matching?: MatchingView;

  constructor() {
  }

  ngOnInit(): void {
  }

}
