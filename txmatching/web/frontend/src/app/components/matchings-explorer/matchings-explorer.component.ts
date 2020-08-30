import { Component, ElementRef, Input, OnInit, ViewChild } from '@angular/core';
import { Matching } from '@app/model/Matching';
import { Patient } from '@app/model/Patient';

@Component({
  selector: 'app-matchings-explorer',
  templateUrl: './matchings-explorer.component.html',
  styleUrls: ['./matchings-explorer.component.scss']
})
export class MatchingsExplorerComponent implements OnInit {

  @ViewChild('scrollable') scrollable?: ElementRef;
  @Input() matchings: Matching[] = [];
  @Input() patients: Patient[] = [];

  public activeMatching?: Matching;

  constructor() {
  }

  ngOnInit(): void {
    this.setActive(this.matchings[0]);
  }

  public setActive(matching: Matching, elementId?: string): void {
    this.activeMatching = matching;
    if (elementId) {
      this._scrollToElement(elementId);
    }
  }

  public getTransplantsCount(matching: Matching): number {
    let sum = 0;
    for (let round of matching.rounds) {
      sum += round.transplants.length;
    }
    return sum;
  }

  private _scrollToElement(elementId: string): void {
    const focusedElement = document.getElementById(elementId);
    console.log(this.scrollable?.nativeElement, focusedElement);
    if (!this.scrollable || !focusedElement) {
      return;
    }

    const scrollable = this.scrollable.nativeElement;
    scrollable.scrollTop = focusedElement.offsetTop;
  }
}
