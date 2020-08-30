import { Component, ElementRef, Input, OnInit, ViewChild } from '@angular/core';
import { MatchingView } from '@app/model/Matching';
import { Patient } from '@app/model/Patient';

@Component({
  selector: 'app-matchings-explorer',
  templateUrl: './matchings-explorer.component.html',
  styleUrls: ['./matchings-explorer.component.scss']
})
export class MatchingsExplorerComponent implements OnInit {

  @ViewChild('scrollable') scrollable?: ElementRef;
  @Input() matchings: MatchingView[] = [];
  @Input() patients: Patient[] = [];

  public activeMatching?: MatchingView;

  constructor() {
  }

  ngOnInit(): void {
    this.setActive(this.matchings.length ? this.matchings[0] : undefined);
  }

  public setActive(matching: MatchingView | undefined): void {
    this.activeMatching = matching;
    if (matching && matching.index) {
      this._scrollToElement(matching.index);
    }
  }

  public getTransplantsCount(matching: MatchingView): number {
    let sum = 0;
    for (let round of matching.rounds) {
      sum += round.transplants.length;
    }
    return sum;
  }

  private _scrollToElement(id: number): void {
    const focusedElement = document.getElementById(`matching-${id}`);
    if (!this.scrollable || !focusedElement) {
      return;
    }

    const scrollable = this.scrollable.nativeElement;
    scrollable.scrollTop = focusedElement.offsetTop;
  }
}
