import { Component, Input, OnInit } from '@angular/core';

@Component({
  selector: 'app-simple-number',
  templateUrl: './simple-number.component.html',
  styleUrls: ['./simple-number.component.scss']
})
export class SimpleNumberComponent implements OnInit {

  @Input() value?: number;
  @Input() label?: string;

  constructor() {
  }

  ngOnInit(): void {
  }

}
