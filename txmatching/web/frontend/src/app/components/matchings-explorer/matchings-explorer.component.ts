import { Component, ElementRef, Input, OnInit, ViewChild } from '@angular/core';
import { matchingBatchSize, MatchingView } from '@app/model/Matching';
import { Patient } from '@app/model/Patient';
import { AppConfiguration } from '@app/model/Configuration';

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
  @Input() configuration?: AppConfiguration;

  public activeMatching?: MatchingView;
  public matchingsInView: MatchingView[] = [];

  ngOnInit(): void {
    this._addMatchingsToView();
    this.setActive(this.matchings.length ? this.matchings[0] : undefined);
  }

  public setActive(matching: MatchingView | undefined): void {
    this.activeMatching = matching;
    if (matching && matching.index) {
      this._scrollToElement(matching.index);
    }
  }

  public onScrollDown(): void {
    this._addMatchingsToView();
  }

  private _scrollToElement(id: number): void {
    const focusedElement = document.getElementById(`matching-${id}`);

    if (!this.list || !focusedElement) {
      return;
    }

    const scrollable = this.list.nativeElement;

    // wait for element to have .active class
    setTimeout(() => {
      scrollable.scrollTop = focusedElement.offsetTop;
    }, 0); // lol yes, 0ms is enough

    if (this.detail) {
      this.detail.nativeElement.scrollTop = 0;
    }
  }

  private _addMatchingsToView(): void {
    const start = this.matchingsInView.length;
    const end = start + matchingBatchSize;
    const matchingsToPush = this.matchings.slice(start, end);
    this.matchingsInView.push(...matchingsToPush);
  }
}
