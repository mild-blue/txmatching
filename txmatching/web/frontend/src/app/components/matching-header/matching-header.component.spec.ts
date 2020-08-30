import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { MatchingHeaderComponent } from './matching-header.component';

describe('MatchingHeaderComponent', () => {
  let component: MatchingHeaderComponent;
  let fixture: ComponentFixture<MatchingHeaderComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [MatchingHeaderComponent]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(MatchingHeaderComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
