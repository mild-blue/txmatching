import { Component, Input } from '@angular/core';

@Component({
  selector: 'flag',
  templateUrl: './flag.component.html',
  styleUrls: ['./flag.component.scss']
})
export class FlagComponent {

  @Input() countryCode?: string;
  public countryParts: string[] = [];

  constructor() {
  }

  ngOnInit() {
    if (this.countryCode) {
      this.countryParts = this.countryCode.split('_');
    }
  }

  get image(): string {
    return `../../../assets/img/countries/${this.countryParts[0]}.png`;
  }
}
