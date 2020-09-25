import { AfterViewInit, Component, ComponentFactoryResolver, ElementRef, Input, OnInit, ViewChild } from '@angular/core';
import { matchingBatchSize, MatchingView } from '@app/model/Matching';
import { PatientList } from '@app/model/Patient';
import { AppConfiguration } from '@app/model/Configuration';
import { ListItem, ListItemDetailComponent, ListItemView } from '@app/components/item-list/item-list.interface';
import { ListItemDirective } from '@app/directives/list-item/list-item.directive';
import { MatchingDetailComponent } from '@app/components/matching-detail/matching-detail.component';
import { ListItemDetailDirective } from '@app/directives/list-item-detail/list-item-detail.directive';
import { MatchingItemComponent } from '@app/components/matching-item/matching-item.component';

@Component({
  selector: 'app-item-list',
  templateUrl: './item-list.component.html',
  styleUrls: ['./item-list.component.scss']
})
export class ItemListComponent implements OnInit, AfterViewInit {

  @ViewChild('list') list?: ElementRef;
  @ViewChild('detail') detail?: ElementRef;

  @ViewChild(ListItemDirective, { static: true }) listItemHost?: ListItemDirective;
  @ViewChild(ListItemDetailDirective, { static: true }) listItemDetailHost?: ListItemDetailDirective;

  @Input() items: ListItem[] = [];
  @Input() patients?: PatientList;
  @Input() configuration?: AppConfiguration;

  @Input() listItemComponent?: typeof MatchingItemComponent;
  @Input() listItemDetailComponent?: typeof MatchingDetailComponent;

  public activeItem?: ListItem;
  public displayedItems: ListItem[] = [];

  public activeAlignedTop: boolean = true;
  public activeAlignedBottom: boolean = false;

  constructor(private _componentFactoryResolver: ComponentFactoryResolver) {
  }

  ngOnInit(): void {
    this._addMatchingsToView();
    this.activeItem = this.displayedItems[0] ?? this.activeItem;
    this._loadDetailComponent(this.activeItem);
  }

  ngAfterViewInit(): void {
    this._initAdjustingStylesOnScroll(this.list, this.detail);
  }

  public setActive(item: ListItem | undefined): void {
    this.activeItem = item;
    if (item && item.index) {
      this._loadDetailComponent(item);
      this._scrollToElement(item.index);
      this.activeAlignedTop = item.index === 1;
    }
  }

  public onScrollDown(): void {
    this._addMatchingsToView();
  }

  public trackMatchingItem(index: number, matching: MatchingView) {
    return matching.index;
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

  private _addMatchingsToView(): void {
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

  private _loadComponents(): void {
    // const componentFactory = this._componentFactoryResolver.resolveComponentFactory(adItem.component);

  }

  private _loadDetailComponent(activeItem: ListItem): void {
    if (!this.listItemDetailComponent) {
      return;
    }

    const detailComponentFactory = this._componentFactoryResolver.resolveComponentFactory(this.listItemDetailComponent);

    if (this.listItemDetailHost) {
      const detailViewContainerRef = this.listItemDetailHost.viewContainerRef;
      detailViewContainerRef.clear();
      const detailComponentRef = detailViewContainerRef.createComponent<ListItemDetailComponent>(detailComponentFactory);
      detailComponentRef.instance.data = activeItem;
      detailComponentRef.instance.patients = this.patients;
    }
  }

  private _loadComponent(item: ListItemView): void {
    // const itemComponentFactory = this._componentFactoryResolver.resolveComponentFactory(item.itemComponent);
    // const detailComponentFactory = this._componentFactoryResolver.resolveComponentFactory(item.detailComponent);

    // if(this.listItemHost) {
    //   const itemViewContainerRef = this.listItemHost.viewContainerRef;
    //   itemViewContainerRef.clear();
    //   const itemComponentRef = itemViewContainerRef.createComponent<ListItemComponent>(itemComponentFactory);
    //   itemComponentRef.instance.data = item.itemData;
    // }
    //
    // if(this.listItemDetailHost) {
    //   const detailViewContainerRef = this.listItemDetailHost.viewContainerRef;
    //   detailViewContainerRef.clear();
    //   const detailComponentRef = detailViewContainerRef.createComponent<ListItemDetailComponent>(detailComponentFactory);
    //   detailComponentRef.instance.data = item.detailData;
    // }
  }
}
