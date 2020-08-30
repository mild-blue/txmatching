import { Component, ElementRef, Input, OnInit, ViewChild } from '@angular/core';
import { MatchingView } from '@app/model/Matching';
import { Patient } from '@app/model/Patient';

@Component({
  selector: 'app-matchings-explorer',
  templateUrl: './matchings-explorer.component.html',
  styleUrls: ['./matchings-explorer.component.scss']
})
export class MatchingsExplorerComponent implements OnInit {

  @ViewChild('list') list?: ElementRef;
  @ViewChild('detail') detail?: ElementRef;

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

  private _scrollToElement(id: number): void {
    const focusedElement = document.getElementById(`matching-${id}`);
    if (!this.list || !focusedElement) {
      return;
    }

    const scrollable = this.list.nativeElement;
    scrollable.scrollTop = focusedElement.offsetTop;

    if (this.detail) {
      this.detail.nativeElement.scrollTop = 0;
    }
  }
}
