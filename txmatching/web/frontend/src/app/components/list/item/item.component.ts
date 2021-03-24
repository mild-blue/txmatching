import { Component, Input, OnInit } from '@angular/core';
import { NewListItem } from '@app/pages/abstract-list/abstract-list.component';

@Component({
  selector: 'app-new-item',
  templateUrl: './item.component.html',
  styleUrls: ['./item.component.scss']
})
export class ItemComponent implements OnInit {

  @Input() isActive: boolean = false;
  @Input() item?: NewListItem;

  constructor() {
  }

  ngOnInit(): void {
  }

}
