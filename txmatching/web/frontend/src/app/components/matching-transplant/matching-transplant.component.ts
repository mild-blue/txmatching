import { Component, Input, OnInit } from '@angular/core';
import { Transplant } from '@app/model/Matching';

@Component({
  selector: 'app-matching-transplant',
  templateUrl: './matching-transplant.component.html',
  styleUrls: ['./matching-transplant.component.scss']
})
export class MatchingTransplantComponent implements OnInit {

  @Input() transplant?: Transplant;

  constructor() {
  }

  ngOnInit(): void {
  }

}
