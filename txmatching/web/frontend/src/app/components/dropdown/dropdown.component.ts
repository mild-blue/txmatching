import { Component, ElementRef, EventEmitter, HostListener, Input, OnInit, Output } from '@angular/core';

@Component({
  selector: 'app-dropdown',
  templateUrl: './dropdown.component.html',
  styleUrls: ['./dropdown.component.scss']
})
export class DropdownComponent implements OnInit {

  @Output() clickedOutside: EventEmitter<boolean> = new EventEmitter<boolean>();
  @Input() open: boolean = false;

  constructor(private _elementRef: ElementRef) {
  }

  ngOnInit(): void {
  }

  @HostListener('document:click', ['$event'])
  clickOut(event: MouseEvent): void {
    if (this.open) {
      if (event.target && !this._elementRef.nativeElement.contains(event.target)) {
        this.clickedOutside.emit(true);
      }
    }
  }

}
