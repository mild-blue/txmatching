import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { MatchingItemComponent } from './matching-item.component';

describe('MatchingItemComponent', () => {
  let component: MatchingItemComponent;
  let fixture: ComponentFixture<MatchingItemComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [MatchingItemComponent]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(MatchingItemComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
