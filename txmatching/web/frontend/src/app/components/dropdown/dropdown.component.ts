import { Component, ElementRef, EventEmitter, Input, OnInit, Output, ViewChild } from '@angular/core';
import * as uuid from 'uuid';

@Component({
  selector: 'app-dropdown',
  templateUrl: './dropdown.component.html',
  styleUrls: ['./dropdown.component.scss']
})
export class DropdownComponent implements OnInit {

  @ViewChild('dropdown') dropdown?: ElementRef;
  @Output() clickedOutside: EventEmitter<boolean> = new EventEmitter<boolean>();
  @Input() open: boolean = false;

  public id: string;

  constructor(private _elementRef: ElementRef) {
    this.id = uuid.v4();
  }

  ngOnInit(): void {
  }

  // todo click outside
  // @HostListener('document:click', ['$event'])
  // clickout(event) {
  //   if(!this.dropdown) {
  //     return;
  //   }
  //   const clickedId = this.dropdown.nativeElement.getAttribute('id');
  //   if(clickedId === this.id) {
  //     console.log("clicked inside", this.id);
  //   }
  // }

}
