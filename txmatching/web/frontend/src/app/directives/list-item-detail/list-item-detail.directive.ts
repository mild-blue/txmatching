import { Directive, ViewContainerRef } from "@angular/core";

@Directive({
  selector: "[listItemDetail]",
})
export class ListItemDetailDirective {
  constructor(public viewContainerRef?: ViewContainerRef) {}
}
