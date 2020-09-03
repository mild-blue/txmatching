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
  public activeAlignedTop: boolean = true;
  public activeAlignedBottom: boolean = false;

  ngOnInit(): void {
    this.activeMatching = this.matchings[0] ?? this.activeMatching;
  }

  ngAfterViewInit(): void {
    this._initAdjustingStylesOnScroll(this.list, this.detail);
  }

  public setActive(matching: MatchingView | undefined): void {
    this.activeMatching = matching;
    if (matching && matching.index) {
      this._scrollToElement(matching.index);
      this.activeAlignedTop = matching.index === 1;
    }
  }

  private _scrollToElement(id: number): void {
    const activeElement = document.getElementById(`matching-${id}`);

    if (!this.list || !activeElement) {
      return;
    }

    const scrollable = this.list.nativeElement;

    // wait for element to have .active class
    setTimeout(() => {
      scrollable.scrollTop = activeElement.offsetTop;
    }, 0); // lol yes, 0ms is enough

    if (this.detail) {
      this.detail.nativeElement.scrollTop = 0;
    }
  }

  private _initAdjustingStylesOnScroll(list?: ElementRef, detail?: ElementRef): void {
    if (!list || !detail) {
      return;
    }

    const listElement = list.nativeElement;
    const detailElement = detail.nativeElement;

    listElement.addEventListener('scroll', (event: WheelEvent) => {
      this._setAlignment(listElement, detailElement);
    });
  }

  private _setAlignment(listElement: HTMLElement, detailItem: HTMLElement): void {
    const activeItem: HTMLElement | null = listElement.querySelector('.active');
    if (!activeItem) {
      return;
    }

    const {
      borderTopLeftRadius,
      borderBottomLeftRadius,
      borderBottomRightRadius,
      borderTopRightRadius
    } = getComputedStyle(activeItem);
    const offsetValue = borderTopLeftRadius || borderBottomLeftRadius || borderBottomRightRadius || borderTopRightRadius;
    const topOffset = Number(offsetValue.replace(/\D+/g, ''));
    const bottomOffset = Number(offsetValue.replace(/\D+/g, ''));

    const detailClientRect = detailItem.getBoundingClientRect();
    const activeItemClientRect = activeItem.getBoundingClientRect();

    const activeTop = activeItemClientRect.top - topOffset;
    const activeBottom = activeItemClientRect.top + activeItem.offsetHeight + bottomOffset;

    const detailTop = detailClientRect.top + topOffset;
    const detailBottom = detailClientRect.top + detailItem.offsetHeight - bottomOffset;

    this.activeAlignedTop = activeTop <= detailTop;
    this.activeAlignedBottom = activeBottom >= detailBottom;
  }
}
