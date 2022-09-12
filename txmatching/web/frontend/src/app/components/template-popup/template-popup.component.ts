import { Component, ElementRef, EventEmitter, Input, OnChanges, Output, SimpleChanges, ViewChild } from "@angular/core";
import { TemplatePopupStyle } from "@app/components/template-popup/template-popup.interface";

@Component({
  selector: "app-template-popup",
  templateUrl: "./template-popup.component.html",
  styleUrls: ["./template-popup.component.scss"],
})
export class TemplatePopupComponent implements OnChanges {
  @Input() title: string = "";
  @Input() isOpened: boolean = false;
  @Input() style: TemplatePopupStyle = TemplatePopupStyle.FullSize;
  @Output() wasClosed: EventEmitter<void> = new EventEmitter<void>();

  @ViewChild("popup") popupElement?: ElementRef;

  constructor() {}

  public ngOnChanges(changes: SimpleChanges): void {
    if (changes && changes.isOpened) {
      const wasOpened = changes.isOpened.previousValue;
      const isOpened = changes.isOpened.currentValue;

      // Scroll content to the top when opened again
      if (!wasOpened && isOpened && this.popupElement) {
        this.popupElement.nativeElement.scrollTop = 0;
      }

      // Toggle body class when opened or closed
      if (!changes.isOpened.firstChange && wasOpened !== isOpened) {
        document.querySelector("body")?.classList.toggle("popup-opened");
      }
    }
  }

  public close(): void {
    this.wasClosed.emit();
  }
}
