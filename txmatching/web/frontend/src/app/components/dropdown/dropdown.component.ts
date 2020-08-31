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
  // clickOut(event: MouseEvent) {
  //   if(!this.dropdown) {
  //     return;
  //   }
  //   const inside = this._elementRef.nativeElement.contains(event.target);
  //   console.log(event.currentTarget)
  //   if(inside) {
  //     console.log("clicked inside", this.id);
  //   } else {
  //     console.log("clicked outside", this.id);
  //   }
  // }
}
