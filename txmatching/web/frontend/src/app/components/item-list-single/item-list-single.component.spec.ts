import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { ItemListSingleComponent } from './item-list-single.component';

describe('ItemListSingleComponent', () => {
  let component: ItemListSingleComponent;
  let fixture: ComponentFixture<ItemListSingleComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ItemListSingleComponent]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(ItemListSingleComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
