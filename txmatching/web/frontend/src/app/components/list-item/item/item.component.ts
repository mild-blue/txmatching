import { Component, ComponentFactoryResolver, Input, OnInit, ViewChild } from '@angular/core';
import { ListItemDirective } from '@app/directives/list-item/list-item.directive';
import { ListItem, ListItemAbstractComponent } from '@app/components/list-item/list-item.interface';
import { PatientList } from '@app/model/Patient';
import { Configuration } from '@app/model/Configuration';

@Component({
  selector: 'app-item',
  templateUrl: './item.component.html',
  styleUrls: ['./item.component.scss']
})
export class ItemComponent implements OnInit {

  @ViewChild(ListItemDirective, { static: true }) listItemHost?: ListItemDirective;

  @Input() listItemComponent?: typeof ListItemAbstractComponent;
  @Input() isActive: boolean = false;
  @Input() item?: ListItem;
  @Input() patients?: PatientList;
  @Input() configuration?: Configuration;

  constructor(private _componentFactoryResolver: ComponentFactoryResolver) {
  }

  ngOnInit(): void {
    this._loadItemComponent(this.item);
  }

  private _loadItemComponent(item?: ListItem): void {
    if (!this.listItemComponent || !item) {
      return;
    }

    const componentFactory = this._componentFactoryResolver.resolveComponentFactory(this.listItemComponent);

    if (this.listItemHost) {
      const viewContainerRef = this.listItemHost.viewContainerRef;
      viewContainerRef.clear();
      const componentRef = viewContainerRef.createComponent<ListItemAbstractComponent>(componentFactory);
      componentRef.instance.item = item;
      componentRef.instance.patients = this.patients;
      componentRef.instance.configuration = this.configuration;
      componentRef.instance.isActive = this.isActive;
    }
  }

}
