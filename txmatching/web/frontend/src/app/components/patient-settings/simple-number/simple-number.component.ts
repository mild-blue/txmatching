import { Component, Input } from "@angular/core";
import { ControlValueAccessor } from "@angular/forms";

@Component({
  selector: "app-simple-number",
  templateUrl: "./simple-number.component.html",
  styleUrls: ["./simple-number.component.scss"],
})
export class SimpleNumberComponent implements ControlValueAccessor {
  @Input() label?: string = "";
  @Input() value?: number;

  get currentValue(): number | undefined {
    return this.value;
  }

  set currentValue(val: number | undefined) {
    this.value = val;
    this.propagateChange(this.value);
  }

  writeValue(val: number | undefined): void {
    if (val !== undefined) {
      this.currentValue = val;
    }
  }

  propagateChange = (e: unknown) => {};

  registerOnChange(fn: (_: unknown) => void) {
    this.propagateChange = fn;
  }

  registerOnTouched() {}
}
