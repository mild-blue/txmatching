import { Directive, ElementRef, HostListener } from "@angular/core";

@Directive({
  selector: "[focusInvalidInput]",
})
export class FormDirective {
  constructor(private _el: ElementRef) {}

  @HostListener("submit")
  onFormSubmit() {
    const invalidControl = this._el.nativeElement.querySelector("input.ng-invalid:not(.no-focus-when-invalid)");

    if (invalidControl) {
      invalidControl.scrollIntoView();
    }
  }
}
