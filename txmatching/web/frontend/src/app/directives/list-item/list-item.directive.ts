import { Directive, ViewContainerRef } from '@angular/core';

@Directive({
  selector: '[listItem]'
})
export class ListItemDirective {

  constructor(public viewContainerRef: ViewContainerRef) {
  }

}
