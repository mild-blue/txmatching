import { Component, Input, OnInit } from '@angular/core';
import { Matching } from '@app/model/Matching';

@Component({
  selector: 'app-matchings-explorer',
  templateUrl: './matchings-explorer.component.html',
  styleUrls: ['./matchings-explorer.component.scss']
})
export class MatchingsExplorerComponent implements OnInit {

  @Input() matchings: Matching[] = [];

  constructor() {
  }

  ngOnInit(): void {
  }

}
