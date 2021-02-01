import { Component, ElementRef, EventEmitter, HostListener, Input, Output } from '@angular/core';

@Component({
  selector: 'app-dropdown',
  templateUrl: './dropdown.component.html',
  styleUrls: ['./dropdown.component.scss']
})
export class DropdownComponent {

  @Output() clickedOutside: EventEmitter<string> = new EventEmitter<string>();

  @Input() open: boolean = false;
  @Input() id: string = '';
  @Input() trigger?: HTMLButtonElement;
  @Input() float: string = "left";

  private _wasClickInside = false;

  constructor(private _elementRef: ElementRef) {
  }

  @HostListener('click')
  clickInside() {
    this._wasClickInside = true;
  }

  @HostListener('document:click', ['$event'])
  clickOut(event: MouseEvent) {
    if (!this.trigger || !this.id) {
      return;
    }

    const clickedElement: Node = event.target as Node;
    const currentDropdown = this._elementRef.nativeElement;

    const insideDropdown = currentDropdown.contains(clickedElement);
    const triggerClicked = this.trigger.contains(clickedElement);

    // We use wasClickInside because contains() do not work properly for elements that are changed by Angular
    if (!triggerClicked && !insideDropdown && !this._wasClickInside) {
      this.clickedOutside.emit(this.id);
    }
    this._wasClickInside = false;
  }
}
