import { AfterViewInit, Component, ElementRef, Input, OnInit, ViewChild } from '@angular/core';
import { MatchingView } from '@app/model/Matching';
import { Patient } from '@app/model/Patient';
import { AppConfiguration } from '@app/model/Configuration';

@Component({
  selector: 'app-matchings-explorer',
  templateUrl: './matchings-explorer.component.html',
  styleUrls: ['./matchings-explorer.component.scss']
})
export class MatchingsExplorerComponent implements OnInit, AfterViewInit {

  @ViewChild('list') list?: ElementRef;
  @ViewChild('detail') detail?: ElementRef;

  @Input() matchings: MatchingView[] = [];
  @Input() patients: Patient[] = [];
  @Input() configuration?: AppConfiguration;

  public activeMatching?: MatchingView;
  public activeAlignedTop: boolean = false;
  public activeAlignedBottom: boolean = false;

  constructor() {
  }

  ngOnInit(): void {
    this.setActive(this.matchings.length ? this.matchings[0] : undefined);
  }

  ngAfterViewInit(): void {
    this._initAdjustingStylesOnScroll(this.list, this.detail);
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

    // wait for element to have .active class
    setTimeout(() => {
      scrollable.scrollTop = focusedElement.offsetTop;
    }, 0); // lol yes, 0ms is enough

    if (this.detail) {
      this.detail.nativeElement.scrollTop = 0;
    }
  }

  private _initAdjustingStylesOnScroll(list?: ElementRef, detail?: ElementRef): void {
    if (!list || !detail) {
      return;
    }

    const tolerance = 40;
    const listElement = list.nativeElement;
    const detailHeight = detail.nativeElement.offsetHeight;
    const detailRectangle = detail.nativeElement.getBoundingClientRect();

    const detailTop = detailRectangle.top + tolerance;
    const detailBottom = detailRectangle.top + detailHeight - tolerance;

    listElement.addEventListener('scroll', (e) => {
      const active = listElement.querySelector('.active');
      if (!active) {
        return;
      }
      const activeHeight = active.offsetHeight;
      const activeRectangle = active.getBoundingClientRect();

      const activeTop = activeRectangle.top - tolerance;
      const activeBottom = activeRectangle.top + activeHeight + tolerance;

      this.activeAlignedTop = activeTop <= detailTop;
      this.activeAlignedBottom = activeBottom >= detailBottom;
    });
  }
}
