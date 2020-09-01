import { Component, Input } from '@angular/core';

@Component({
  selector: 'flag',
  templateUrl: './flag.component.html',
  styleUrls: ['./flag.component.scss']
})
export class FlagComponent {

  @Input() countryCode?: string;

  constructor() {
  }

  get image(): string {
    return `../../../assets/img/countries/${this.countryCode}.png`;
  }
}
