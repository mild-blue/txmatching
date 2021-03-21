import { AfterViewInit, Component, ElementRef, OnChanges, OnInit, SimpleChanges, ViewChild } from '@angular/core';
import { matchingBatchSize } from '@app/model';
import { scrollableDetailClass } from '@app/services/ui-interactions/ui-iteractions';
import { UiInteractionsService } from '@app/services/ui-interactions/ui-interactions.service';

export interface NewListItem {
  index: number;
  isActive?: boolean;
}

@Component({ template: '' })
export class AbstractListComponent implements OnInit, OnChanges, AfterViewInit {

  public saveLastViewedItem: boolean = false;
  public useInfiniteScroll: boolean = true;

  public items: NewListItem[] = [];
  public active?: NewListItem;

  @ViewChild('list') list?: ElementRef;
  @ViewChild('detail') detail?: ElementRef;

  public activeItem?: NewListItem;
  public displayedItems: NewListItem[] = [];

  public activeAlignedTop: boolean = true;
  public activeAlignedBottom: boolean = false;

  public scrollableDetailClass: string = scrollableDetailClass;
  public enableSmoothScroll: boolean = true;

  constructor(protected _uiInteractionsService: UiInteractionsService) {
  }

  ngOnInit(): void {
    // this.reloadItems();
  }

  ngOnChanges(changes: SimpleChanges) {
    console.log('on changes');
    if (changes.items) {
      this.reloadItems(changes.items.currentValue);
    }
  }

  ngAfterViewInit(): void {
    this._initAdjustingStylesOnScroll(this.list, this.detail);

    if (this.activeItem) {
      this._scrollToElement(this.activeItem.index);
    }
  }

  public handleItemClick(item: NewListItem): void {
    this.enableSmoothScroll = true;
    this.setActive(item);
  }

  public setActive(item: NewListItem | undefined): void {

    // return if clicked on the same item
    if (this.activeItem === item) {
      return;
    }

    // deactivate activeItem if there is one
    if (this.activeItem) {
      this.activeItem.isActive = false;
    }

    // activate new item
    this.activeItem = item;
    if (item?.index) {
      item.isActive = true;
      this.activeAlignedTop = true;
      // this._loadDetailComponent();
      this._scrollToElement(item.index);

      // save last clicked patient pair
      if (this.saveLastViewedItem && this._uiInteractionsService.getLastViewedItemId() !== item.index) {
        this._uiInteractionsService.setLastViewedPair(item.index);
      }
    }
  }

  public onScrollDown(): void {
    this._addItemsBatchToView();
  }

  public trackListItem(index: number, item: NewListItem) {
    return item.index;
  }

  private _scrollToElement(id: number): void {
    const activeElement = document.getElementById(`list-item-${id}`);

    if (!this.list || !activeElement) {
      return;
    }

    const scrollable = this.list.nativeElement;

    // wait for element to have .active class
    setTimeout(() => {
      scrollable.scrollTop = activeElement.offsetTop;
    }, 10); // wait 10ms for execution, see https://stackoverflow.com/a/779785/7169288

    if (this.detail) {
      this.detail.nativeElement.scrollTop = 0;
    }
  }

  private _addItemsBatchToView(): void {
    const start = this.displayedItems.length;
    const end = start + matchingBatchSize;
    const matchingsToPush = this.items.slice(start, end);
    this.displayedItems.push(...matchingsToPush);
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

  public reloadItems(items: NewListItem[]): void {
    this.items = [...items];
    console.log('Reloading', this.items);
    if (this.useInfiniteScroll) {
      this.displayedItems = [];
      this._addItemsBatchToView();
    } else if (!this.displayedItems.length) { // first loading
      this.enableSmoothScroll = false;
      this.displayedItems = this.items;
    }

    // set first or saved item as active if not set from @Input()
    let newActiveItem = this.active;
    if (!this.active) {
      newActiveItem = this.displayedItems[0];
      if (this.saveLastViewedItem && this.items.length) {
        const lastViewedId = this._uiInteractionsService.getLastViewedItemId();
        const foundItem = this.items.find(item => item.index === lastViewedId);
        newActiveItem = foundItem ?? newActiveItem;
      }
    }

    this.setActive(newActiveItem);
  }

}
