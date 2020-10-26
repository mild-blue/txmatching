import { AfterViewInit, Component, ComponentFactoryResolver, ElementRef, Input, OnChanges, SimpleChanges, ViewChild } from '@angular/core';
import { matchingBatchSize } from '@app/model/Matching';
import { AppConfiguration } from '@app/model/Configuration';
import { ListItem, ListItemAbstractComponent, ListItemDetailAbstractComponent } from '@app/components/list-item/list-item.interface';
import { ListItemDetailDirective } from '@app/directives/list-item-detail/list-item-detail.directive';
import { PatientList } from '@app/model/PatientList';

@Component({
  selector: 'app-item-list',
  templateUrl: './list-item.component.html',
  styleUrls: ['./list-item.component.scss']
})
export class ListItemComponent implements OnChanges, AfterViewInit {

  @ViewChild('list') list?: ElementRef;
  @ViewChild('detail') detail?: ElementRef;

  @ViewChild(ListItemDetailDirective, { static: true }) listItemDetailHost?: ListItemDetailDirective;

  @Input() items: ListItem[] = [];
  @Input() patients?: PatientList;
  @Input() configuration?: AppConfiguration;

  @Input() listItemComponent?: typeof ListItemAbstractComponent;
  @Input() listItemDetailComponent?: typeof ListItemDetailAbstractComponent;

  public activeItem?: ListItem;
  public displayedItems: ListItem[] = [];

  public activeAlignedTop: boolean = true;
  public activeAlignedBottom: boolean = false;

  constructor(private _componentFactoryResolver: ComponentFactoryResolver) {
  }

  ngOnChanges(changes: SimpleChanges) {
    if (changes.listItemDetailComponent) {
      this._loadDetailComponent();
    }

    if (changes.items) {
      this.items = changes.items.currentValue;
      this._reloadItems();
    }
  }

  ngAfterViewInit(): void {
    this._initAdjustingStylesOnScroll(this.list, this.detail);
  }

  public setActive(item: ListItem | undefined): void {

    // deactivate activeItem if there is one
    if (this.activeItem) {
      this.activeItem.isActive = false;
    }

    // activate new item
    this.activeItem = item;
    if (item && item.index) {
      item.isActive = true;
      this._loadDetailComponent();
      this._scrollToElement(item.index);
      this.activeAlignedTop = item.index === 1;
    }
  }

  public onScrollDown(): void {
    this._addItemsBatchToView();
  }

  public trackListItem(index: number, item: ListItem) {
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

  private _reloadItems(): void {
    this.displayedItems = [];
    this._addItemsBatchToView();
    this.setActive(this.displayedItems[0]);
    this._loadDetailComponent();
  }

  private _loadDetailComponent(): void {
    const activeItem = this.activeItem;
    if (!this.listItemDetailComponent || !activeItem) {
      return;
    }

    const detailComponentFactory = this._componentFactoryResolver.resolveComponentFactory(this.listItemDetailComponent);

    if (this.listItemDetailHost) {
      const detailViewContainerRef = this.listItemDetailHost.viewContainerRef;
      detailViewContainerRef.clear();
      const detailComponentRef = detailViewContainerRef.createComponent<ListItemDetailAbstractComponent>(detailComponentFactory);
      detailComponentRef.instance.item = activeItem;
      detailComponentRef.instance.patients = this.patients;
    }
  }
}
