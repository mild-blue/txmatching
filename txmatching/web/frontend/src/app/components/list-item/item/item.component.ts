import {
  Component,
  ComponentFactoryResolver,
  ComponentRef,
  Input,
  OnChanges,
  OnInit,
  SimpleChanges,
  ViewChild,
} from "@angular/core";
import { ListItemDirective } from "@app/directives/list-item/list-item.directive";
import { ListItem, ListItemAbstractComponent } from "@app/components/list-item/list-item.interface";
import { Configuration } from "@app/model/Configuration";
import { PatientList } from "@app/model/PatientList";

@Component({
  selector: "app-item",
  templateUrl: "./item.component.html",
  styleUrls: ["./item.component.scss"],
})
export class ItemComponent implements OnInit, OnChanges {
  private _componentRef?: ComponentRef<ListItemAbstractComponent>;

  @ViewChild(ListItemDirective, { static: true }) listItemHost?: ListItemDirective;

  @Input() listItemComponent?: typeof ListItemAbstractComponent;
  @Input() isActive: boolean = false;
  @Input() item?: ListItem;
  @Input() patients?: PatientList;
  @Input() configuration?: Configuration;

  constructor(private _componentFactoryResolver: ComponentFactoryResolver) {}

  ngOnInit(): void {
    this._loadItemComponent();
  }

  ngOnChanges(changes: SimpleChanges) {
    if (changes.listItemComponent || changes.isActive) {
      this._loadItemComponent();
    }
    if (changes.item) {
      this.item = changes.item.currentValue;
      this._loadItemComponent();
    }
  }

  private _loadItemComponent(): void {
    const item = this.item;
    if (!this.listItemComponent || !item) {
      return;
    }

    const componentFactory = this._componentFactoryResolver.resolveComponentFactory(this.listItemComponent);

    if (this.listItemHost) {
      const viewContainerRef = this.listItemHost.viewContainerRef;
      viewContainerRef.clear();
      this._componentRef = viewContainerRef.createComponent<ListItemAbstractComponent>(componentFactory);
      this._componentRef.instance.item = item;
      this._componentRef.instance.isActive = this.isActive;
      this._componentRef.instance.patients = this.patients;
      this._componentRef.instance.configuration = this.configuration;
    }
  }
}
